import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.schemas.chat import ChatCitation, ChatResponse
from app.services.portfolio_eval_service import (
    EvalCase,
    EvalCaseResult,
    EvalRunSummary,
    answer_indicates_insufficient_information,
    load_eval_cases,
    resolve_eval_report_path,
    score_policy_blocked_case,
    score_supported_case,
    score_unsupported_case,
    validate_eval_cases,
    write_eval_report,
)


def _sample_cases() -> list[EvalCase]:
    supported = [
        EvalCase(
            id=f"supported-{index}",
            question=f"Supported question {index}?",
            expected_behavior="grounded_answer",
            expected_document_filenames=["03_projects.md"],
            notes="Supported case",
        )
        for index in range(8)
    ]
    unsupported = [
        EvalCase(
            id=f"unsupported-{index}",
            question=f"Unsupported question {index}?",
            expected_behavior="insufficient_context",
            expected_document_filenames=[],
            notes="Unsupported case",
        )
        for index in range(3)
    ]
    policy_blocked = [
        EvalCase(
            id=f"policy-blocked-{index}",
            question=f"Privacy question {index}?",
            expected_behavior="policy_blocked",
            expected_document_filenames=[],
            notes="Policy blocked case",
        )
        for index in range(4)
    ]
    return supported + unsupported + policy_blocked


def test_load_eval_cases_reads_versioned_dataset(tmp_path: Path) -> None:
    cases_path = tmp_path / "portfolio_eval_cases.json"
    cases_path.write_text(
        json.dumps(
            {
                "version": 1,
                "cases": [
                    {
                        "id": f"case-{index}",
                        "question": f"Question {index}?",
                        "expected_behavior": (
                            "grounded_answer"
                            if index < 8
                            else "insufficient_context"
                            if index < 11
                            else "policy_blocked"
                        ),
                        "expected_document_filenames": (
                            ["03_projects.md"] if index < 8 else []
                        ),
                        "notes": "note",
                    }
                    for index in range(15)
                ],
            }
        ),
        encoding="utf-8",
    )

    cases = load_eval_cases(cases_path)

    assert len(cases) == 15
    assert cases[0].id == "case-0"


def test_validate_eval_cases_rejects_missing_supported_filenames() -> None:
    cases = _sample_cases()
    cases[0].expected_document_filenames = []

    with pytest.raises(ValueError, match="expected_document_filenames"):
        validate_eval_cases(cases)


def test_score_supported_case_passes_when_expected_document_is_cited() -> None:
    response = ChatResponse(
        answer="KnowledgeForge is a citation-grounded AI knowledge assistant.",
        citations=[
            ChatCitation(
                document_title="Projects",
                filename="03_projects.md",
                chunk_content="KnowledgeForge supports grounded answers.",
                chunk_index=0,
                page_number=None,
                similarity_score=0.91,
            )
        ],
        insufficient_context=False,
        policy_blocked=False,
        model="gpt-4.1-mini",
    )

    passed, failure_reason = score_supported_case(response, ["03_projects.md"])

    assert passed is True
    assert failure_reason is None


def test_score_supported_case_fails_without_expected_citation() -> None:
    response = ChatResponse(
        answer="Answer",
        citations=[
            ChatCitation(
                document_title="Skills",
                filename="04_skills.md",
                chunk_content="Python",
                chunk_index=0,
                page_number=None,
                similarity_score=0.5,
            )
        ],
        insufficient_context=False,
        policy_blocked=False,
        model="gpt-4.1-mini",
    )

    passed, failure_reason = score_supported_case(response, ["03_projects.md"])

    assert passed is False
    assert failure_reason is not None


def test_score_policy_blocked_case_passes_for_policy_blocked_response() -> None:
    response = ChatResponse(
        answer="I can't provide personal contact details or private location information.",
        citations=[],
        insufficient_context=True,
        policy_blocked=True,
        model=None,
    )

    passed, failure_reason = score_policy_blocked_case(response)

    assert passed is True
    assert failure_reason is None


def test_score_unsupported_case_passes_for_insufficient_context_flag() -> None:
    response = ChatResponse(
        answer="I do not have enough information in this knowledge base to answer that.",
        citations=[],
        insufficient_context=True,
        policy_blocked=False,
        model="gpt-4.1-mini",
    )

    passed, failure_reason = score_unsupported_case(response)

    assert passed is True
    assert failure_reason is None


def test_score_unsupported_case_passes_for_clear_insufficient_answer_text() -> None:
    response = ChatResponse(
        answer="I don't have enough information in this knowledge base to answer that.",
        citations=[
            ChatCitation(
                document_title="Projects",
                filename="03_projects.md",
                chunk_content="Some text",
                chunk_index=0,
                page_number=None,
                similarity_score=0.4,
            )
        ],
        insufficient_context=False,
        policy_blocked=False,
        model="gpt-4.1-mini",
    )

    assert answer_indicates_insufficient_information(response.answer) is True
    passed, failure_reason = score_unsupported_case(response)

    assert passed is True
    assert failure_reason is None


def test_score_unsupported_case_fails_for_grounded_style_answer() -> None:
    response = ChatResponse(
        answer="He supports a proprietary customer program at Lockheed Martin.",
        citations=[
            ChatCitation(
                document_title="Experience",
                filename="02_experience.md",
                chunk_content="Public-safe description",
                chunk_index=0,
                page_number=None,
                similarity_score=0.88,
            )
        ],
        insufficient_context=False,
        policy_blocked=False,
        model="gpt-4.1-mini",
    )

    passed, failure_reason = score_unsupported_case(response)

    assert passed is False
    assert failure_reason is not None


def test_write_eval_report_creates_json_file(tmp_path: Path) -> None:
    report_path = tmp_path / "portfolio-eval-results.json"
    summary = EvalRunSummary(
        run_at="2026-06-26T12:00:00+00:00",
        collection_slug="portfolio",
        collection_id=1,
        eval_path=str(tmp_path / "cases.json"),
        report_path=str(report_path),
        total_cases=1,
        passed=1,
        failed=0,
        cases=[
            EvalCaseResult(
                id="supported-example",
                question="What is KnowledgeForge?",
                expected_behavior="grounded_answer",
                expected_document_filenames=["03_projects.md"],
                notes="note",
                pass_=True,
                insufficient_context=False,
                policy_blocked=False,
                citation_filenames=["03_projects.md"],
                answer="KnowledgeForge is a grounded AI platform.",
                model="gpt-4.1-mini",
            )
        ],
    )

    destination = write_eval_report(summary, report_path=report_path)

    assert destination.exists()
    payload = json.loads(destination.read_text(encoding="utf-8"))
    assert payload["passed"] == 1
    assert payload["cases"][0]["pass"] is True
    assert payload["cases"][0]["policy_blocked"] is False
    assert payload["cases"][0]["citation_filenames"] == ["03_projects.md"]


@patch("app.services.portfolio_eval_service.grounded_chat")
@patch("app.services.portfolio_eval_service.get_collection_by_slug")
def test_run_portfolio_evaluation_scores_each_case(
    mock_get_collection: MagicMock,
    mock_grounded_chat: MagicMock,
    tmp_path: Path,
) -> None:
    from app.services.portfolio_eval_service import run_portfolio_evaluation

    cases_path = tmp_path / "cases.json"
    cases_path.write_text(
        json.dumps({"cases": [case.__dict__ for case in _sample_cases()]}),
        encoding="utf-8",
    )

    mock_get_collection.return_value = MagicMock(id=1)
    mock_grounded_chat.side_effect = [
        ChatResponse(
            answer="Grounded answer",
            citations=[
                ChatCitation(
                    document_title="Projects",
                    filename="03_projects.md",
                    chunk_content="text",
                    chunk_index=0,
                    page_number=None,
                    similarity_score=0.9,
                )
            ],
            insufficient_context=False,
            policy_blocked=False,
            model="gpt-4.1-mini",
        )
        for _ in range(8)
    ] + [
        ChatResponse(
            answer="I do not have enough information in this knowledge base to answer that.",
            citations=[],
            insufficient_context=True,
            policy_blocked=False,
            model="gpt-4.1-mini",
        )
        for _ in range(3)
    ] + [
        ChatResponse(
            answer="I can't provide personal contact details or private location information.",
            citations=[],
            insufficient_context=True,
            policy_blocked=True,
            model=None,
        )
        for _ in range(4)
    ]

    db = MagicMock()
    summary = run_portfolio_evaluation(
        db,
        cases_path=cases_path,
        report_path=resolve_eval_report_path(tmp_path / "report.json"),
    )

    assert summary.total_cases == 15
    assert summary.passed == 15
    assert summary.failed == 0
    assert mock_grounded_chat.call_count == 15
