from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import INSUFFICIENT_ANSWER, grounded_chat
from app.services.document_service import get_collection_by_slug
from app.services.portfolio_import_service import PORTFOLIO_COLLECTION_SLUG

VALID_EXPECTED_BEHAVIORS = {"grounded_answer", "insufficient_context", "policy_blocked"}
MIN_CASE_COUNT = 15
MIN_SUPPORTED_CASE_COUNT = 8
MIN_UNSUPPORTED_CASE_COUNT = 3
MIN_POLICY_BLOCKED_CASE_COUNT = 4


@dataclass
class EvalCase:
    id: str
    question: str
    expected_behavior: str
    expected_document_filenames: list[str]
    notes: str


@dataclass
class EvalCaseResult:
    id: str
    question: str
    expected_behavior: str
    expected_document_filenames: list[str]
    notes: str
    pass_: bool
    insufficient_context: bool
    policy_blocked: bool
    citation_filenames: list[str]
    answer: str
    model: str | None
    failure_reason: str | None = None

    def to_report_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["pass"] = payload.pop("pass_")
        return payload


@dataclass
class EvalRunSummary:
    run_at: str
    collection_slug: str
    collection_id: int
    eval_path: str
    report_path: str
    total_cases: int
    passed: int
    failed: int
    cases: list[EvalCaseResult] = field(default_factory=list)


def resolve_eval_cases_path(cases_path: Path | None = None) -> Path:
    if cases_path is not None:
        return cases_path.resolve()

    repo_root = Path(__file__).resolve().parents[4]
    return (repo_root / "docs" / "evals" / "portfolio_eval_cases.json").resolve()


def resolve_eval_report_path(report_path: Path | None = None) -> Path:
    if report_path is not None:
        return report_path.resolve()

    repo_root = Path(__file__).resolve().parents[4]
    return (repo_root / "reports" / "portfolio-eval-results.json").resolve()


def load_eval_cases(cases_path: Path | None = None) -> list[EvalCase]:
    resolved_path = resolve_eval_cases_path(cases_path)
    payload = json.loads(resolved_path.read_text(encoding="utf-8"))
    raw_cases = payload.get("cases", payload if isinstance(payload, list) else None)

    if not isinstance(raw_cases, list):
        raise ValueError("Evaluation dataset must contain a 'cases' array.")

    cases = [
        EvalCase(
            id=str(item["id"]),
            question=str(item["question"]),
            expected_behavior=str(item["expected_behavior"]),
            expected_document_filenames=list(item.get("expected_document_filenames", [])),
            notes=str(item.get("notes", "")),
        )
        for item in raw_cases
    ]
    validate_eval_cases(cases)
    return cases


def validate_eval_cases(cases: list[EvalCase]) -> None:
    if len(cases) < MIN_CASE_COUNT:
        raise ValueError(f"Evaluation dataset must include at least {MIN_CASE_COUNT} cases.")

    supported_count = sum(
        1 for case in cases if case.expected_behavior == "grounded_answer"
    )
    unsupported_count = sum(
        1 for case in cases if case.expected_behavior == "insufficient_context"
    )
    policy_blocked_count = sum(
        1 for case in cases if case.expected_behavior == "policy_blocked"
    )

    if supported_count < MIN_SUPPORTED_CASE_COUNT:
        raise ValueError(
            "Evaluation dataset must include at least "
            f"{MIN_SUPPORTED_CASE_COUNT} grounded_answer cases."
        )

    if unsupported_count < MIN_UNSUPPORTED_CASE_COUNT:
        raise ValueError(
            "Evaluation dataset must include at least "
            f"{MIN_UNSUPPORTED_CASE_COUNT} insufficient_context cases."
        )

    if policy_blocked_count < MIN_POLICY_BLOCKED_CASE_COUNT:
        raise ValueError(
            "Evaluation dataset must include at least "
            f"{MIN_POLICY_BLOCKED_CASE_COUNT} policy_blocked cases."
        )

    seen_ids: set[str] = set()
    for case in cases:
        if not case.id.strip():
            raise ValueError("Each evaluation case must include a non-empty id.")
        if case.id in seen_ids:
            raise ValueError(f"Duplicate evaluation case id: {case.id}")
        seen_ids.add(case.id)

        if not case.question.strip():
            raise ValueError(f"Case '{case.id}' must include a non-empty question.")

        if case.expected_behavior not in VALID_EXPECTED_BEHAVIORS:
            raise ValueError(
                f"Case '{case.id}' has invalid expected_behavior: "
                f"{case.expected_behavior}"
            )

        if case.expected_behavior == "grounded_answer" and not case.expected_document_filenames:
            raise ValueError(
                f"Case '{case.id}' must include expected_document_filenames."
            )

        if case.expected_behavior in {"insufficient_context", "policy_blocked"} and case.expected_document_filenames:
            raise ValueError(
                f"Case '{case.id}' should not include expected_document_filenames."
            )


def answer_indicates_insufficient_information(answer: str) -> bool:
    normalized = answer.strip().lower()
    if normalized == INSUFFICIENT_ANSWER.lower():
        return True

    phrases = (
        "do not have enough information",
        "don't have enough information",
        "does not have enough information",
        "not enough information in this knowledge base",
        "cannot answer",
        "can't answer",
        "no information in this knowledge base",
    )
    return any(phrase in normalized for phrase in phrases)


def score_supported_case(
    response: ChatResponse,
    expected_document_filenames: list[str],
) -> tuple[bool, str | None]:
    if response.insufficient_context:
        return False, "Expected a grounded answer but insufficient_context was true."

    cited_filenames = {citation.filename for citation in response.citations}
    expected_filenames = set(expected_document_filenames)

    if not cited_filenames.intersection(expected_filenames):
        return (
            False,
            "Expected at least one citation from "
            f"{sorted(expected_filenames)} but received {sorted(cited_filenames)}.",
        )

    return True, None


def score_policy_blocked_case(response: ChatResponse) -> tuple[bool, str | None]:
    if response.policy_blocked:
        return True, None

    if response.insufficient_context and answer_indicates_insufficient_information(
        response.answer
    ):
        return True, None

    return (
        False,
        "Expected a privacy policy block or insufficient-context response.",
    )


def score_unsupported_case(response: ChatResponse) -> tuple[bool, str | None]:
    if response.insufficient_context:
        return True, None

    if answer_indicates_insufficient_information(response.answer):
        return True, None

    return (
        False,
        "Expected an insufficient-context response but received a grounded-style answer.",
    )


def score_eval_case(case: EvalCase, response: ChatResponse) -> EvalCaseResult:
    if case.expected_behavior == "grounded_answer":
        passed, failure_reason = score_supported_case(
            response,
            case.expected_document_filenames,
        )
    elif case.expected_behavior == "policy_blocked":
        passed, failure_reason = score_policy_blocked_case(response)
    else:
        passed, failure_reason = score_unsupported_case(response)

    return EvalCaseResult(
        id=case.id,
        question=case.question,
        expected_behavior=case.expected_behavior,
        expected_document_filenames=case.expected_document_filenames,
        notes=case.notes,
        pass_=passed,
        insufficient_context=response.insufficient_context,
        policy_blocked=response.policy_blocked,
        citation_filenames=[citation.filename for citation in response.citations],
        answer=response.answer,
        model=response.model,
        failure_reason=failure_reason,
    )


def run_portfolio_evaluation(
    db: Session,
    *,
    cases_path: Path | None = None,
    report_path: Path | None = None,
    retrieval_limit: int = 5,
) -> EvalRunSummary:
    cases = load_eval_cases(cases_path)
    collection = get_collection_by_slug(db, PORTFOLIO_COLLECTION_SLUG)
    if collection is None:
        raise ValueError(
            f'Portfolio collection with slug "{PORTFOLIO_COLLECTION_SLUG}" was not found.'
        )

    results: list[EvalCaseResult] = []
    for case in cases:
        response = grounded_chat(
            db,
            ChatRequest(
                collection_id=collection.id,
                question=case.question,
                retrieval_limit=retrieval_limit,
            ),
        )
        results.append(score_eval_case(case, response))

    summary = EvalRunSummary(
        run_at=datetime.now(UTC).isoformat(),
        collection_slug=PORTFOLIO_COLLECTION_SLUG,
        collection_id=collection.id,
        eval_path=str(resolve_eval_cases_path(cases_path)),
        report_path=str(resolve_eval_report_path(report_path)),
        total_cases=len(results),
        passed=sum(1 for result in results if result.pass_),
        failed=sum(1 for result in results if not result.pass_),
        cases=results,
    )
    write_eval_report(summary, report_path=report_path)
    return summary


def write_eval_report(
    summary: EvalRunSummary,
    *,
    report_path: Path | None = None,
) -> Path:
    destination = resolve_eval_report_path(report_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "run_at": summary.run_at,
        "collection_slug": summary.collection_slug,
        "collection_id": summary.collection_id,
        "eval_path": summary.eval_path,
        "report_path": str(destination),
        "total_cases": summary.total_cases,
        "passed": summary.passed,
        "failed": summary.failed,
        "cases": [case.to_report_dict() for case in summary.cases],
    }
    destination.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return destination


def print_eval_summary(summary: EvalRunSummary, *, verbose: bool = False) -> None:
    print(f"Portfolio evaluation run: {summary.run_at}")
    print(f"Collection: {summary.collection_slug} (id={summary.collection_id})")
    print(f"Eval dataset: {summary.eval_path}")
    print(f"Report: {summary.report_path}")
    print(f"Results: {summary.passed}/{summary.total_cases} passed")
    print("")

    for result in summary.cases:
        status = "PASS" if result.pass_ else "FAIL"
        print(f"[{status}] {result.id}")
        print(f"  question: {result.question}")
        print(f"  expected: {result.expected_behavior}")
        print(f"  insufficient_context: {result.insufficient_context}")
        print(f"  policy_blocked: {result.policy_blocked}")
        print(f"  citations: {result.citation_filenames or '[]'}")
        if result.failure_reason:
            print(f"  failure: {result.failure_reason}")
        if verbose:
            print(f"  answer: {result.answer}")
            if result.citation_filenames:
                print("  citation details:")
                for filename in result.citation_filenames:
                    print(f"    - {filename}")
        print("")

    if summary.failed:
        print(f"Evaluation completed with {summary.failed} failing case(s).")
    else:
        print("Evaluation completed successfully.")
