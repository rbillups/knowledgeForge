#!/usr/bin/env python3
"""CLI for running the Portfolio Knowledge Base grounded-chat evaluation suite."""

from __future__ import annotations

import argparse
import sys

from app.database.session import SessionLocal
from app.services.portfolio_eval_service import (
    print_eval_summary,
    run_portfolio_evaluation,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run the Portfolio Knowledge Base evaluation suite against the "
            "grounded chat service."
        ),
    )
    parser.add_argument(
        "--cases-path",
        type=str,
        default=None,
        help="Path to the portfolio evaluation JSON dataset.",
    )
    parser.add_argument(
        "--report-path",
        type=str,
        default=None,
        help="Path for the JSON evaluation report output.",
    )
    parser.add_argument(
        "--retrieval-limit",
        type=int,
        default=5,
        help="Retrieval limit passed to grounded chat for each case.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print answers and citation filenames for every case.",
    )
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with a non-zero status code if any case fails.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    db = SessionLocal()
    try:
        summary = run_portfolio_evaluation(
            db,
            cases_path=args.cases_path,
            report_path=args.report_path,
            retrieval_limit=args.retrieval_limit,
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    finally:
        db.close()

    print_eval_summary(summary, verbose=args.verbose)

    if args.fail_on_error and summary.failed > 0:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
