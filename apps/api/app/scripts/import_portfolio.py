#!/usr/bin/env python3
"""CLI for seeding the Portfolio Knowledge Base from Markdown source files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from app.database.session import SessionLocal
from app.services.portfolio_import_service import (
    PortfolioImportFilePlan,
    PortfolioImportFileResult,
    PortfolioImportSummary,
    import_portfolio_pack,
    resolve_portfolio_source_dir,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Import public-safe portfolio Markdown files into the "
            'Portfolio Knowledge Base collection (slug: "portfolio").'
        ),
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=None,
        help="Directory containing portfolio Markdown files.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List files that would be imported without writing to the database.",
    )
    return parser


def print_summary(summary: PortfolioImportSummary) -> None:
    print(f"Portfolio source directory: {summary.source_dir}")
    print(f"Mode: {'dry-run' if summary.dry_run else 'import'}")
    print(f"Found source files: {len(summary.files)}")
    print("")

    for item in summary.files:
        if isinstance(item, PortfolioImportFilePlan):
            existing_note = (
                f" (existing document id: {item.existing_document_id})"
                if item.existing_document_id is not None
                else ""
            )
            print(
                f"[dry-run] {item.filename} -> {item.title} "
                f"({item.action}){existing_note}"
            )
            continue

        status = "SUCCESS" if item.success else "FAILED"
        print(f"[{status}] {item.filename} -> {item.title} ({item.action})")
        if item.success:
            print(f"  chunks created: {item.chunk_count}")
            print(f"  embedding status: {item.embedding_status}")
        else:
            print(f"  error: {item.error}")
        print("")

    if not summary.dry_run:
        print(
            f"Import complete: {summary.succeeded} succeeded, "
            f"{summary.failed} failed."
        )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    source_dir = resolve_portfolio_source_dir(args.source_dir)

    db = SessionLocal()
    try:
        summary = import_portfolio_pack(
            db,
            source_dir=source_dir,
            dry_run=args.dry_run,
        )
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        message = exc.message if hasattr(exc, "message") else str(exc)
        print(f"Error: {message}", file=sys.stderr)
        return 1
    finally:
        db.close()

    print_summary(summary)
    return 0 if summary.dry_run or summary.failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
