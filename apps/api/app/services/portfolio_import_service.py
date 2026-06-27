from dataclasses import dataclass, field
from pathlib import Path

from sqlalchemy.orm import Session

PORTFOLIO_COLLECTION_SLUG = "portfolio"
PORTFOLIO_SOURCE_TYPE = "portfolio"

READABLE_TITLES: dict[str, str] = {
    "01_about.md": "About",
    "02_experience.md": "Professional Experience",
    "03_projects.md": "Projects",
    "04_skills.md": "Skills",
    "05_education.md": "Education",
    "06_career-focus.md": "Career Focus",
    "07_contact.md": "Contact",
}


@dataclass
class PortfolioImportFilePlan:
    source_path: Path
    filename: str
    title: str
    action: str
    existing_document_id: int | None = None


@dataclass
class PortfolioImportFileResult:
    filename: str
    title: str
    action: str
    chunk_count: int = 0
    embedding_status: str = "not_started"
    success: bool = True
    error: str | None = None


@dataclass
class PortfolioImportSummary:
    source_dir: Path
    dry_run: bool
    files: list[PortfolioImportFileResult | PortfolioImportFilePlan] = field(
        default_factory=list
    )

    @property
    def succeeded(self) -> int:
        return sum(
            1
            for item in self.files
            if isinstance(item, PortfolioImportFileResult) and item.success
        )

    @property
    def failed(self) -> int:
        return sum(
            1
            for item in self.files
            if isinstance(item, PortfolioImportFileResult) and not item.success
        )


def resolve_portfolio_source_dir(source_dir: Path | None = None) -> Path:
    if source_dir is not None:
        return source_dir.resolve()

    repo_root = Path(__file__).resolve().parents[4]
    return (repo_root / "docs" / "portfolio-source").resolve()


def discover_portfolio_source_files(source_dir: Path) -> list[Path]:
    if not source_dir.exists():
        raise FileNotFoundError(f"Portfolio source directory not found: {source_dir}")

    return sorted(source_dir.glob("*.md"))


def readable_title_for_filename(filename: str) -> str:
    if filename in READABLE_TITLES:
        return READABLE_TITLES[filename]

    stem = Path(filename).stem
    if "_" in stem:
        stem = stem.split("_", 1)[1]
    return stem.replace("-", " ").title()


class PortfolioCollectionNotFoundError(Exception):
    message = (
        'Knowledge collection with slug "portfolio" was not found. '
        "Apply the database schema seed before importing."
    )

    def __init__(self) -> None:
        super().__init__(self.message)


def import_portfolio_pack(
    db: Session,
    *,
    source_dir: Path | None = None,
    dry_run: bool = False,
) -> PortfolioImportSummary:
    from app.services.document_service import (
        find_document_in_collection,
        get_collection_by_slug,
        import_markdown_file,
    )

    resolved_source_dir = resolve_portfolio_source_dir(source_dir)
    source_files = discover_portfolio_source_files(resolved_source_dir)
    summary = PortfolioImportSummary(
        source_dir=resolved_source_dir,
        dry_run=dry_run,
    )

    collection = get_collection_by_slug(db, PORTFOLIO_COLLECTION_SLUG)
    if collection is None:
        raise PortfolioCollectionNotFoundError()

    for source_path in source_files:
        filename = source_path.name
        title = readable_title_for_filename(filename)
        existing = find_document_in_collection(
            db,
            collection_id=collection.id,
            filename=filename,
            source_type=PORTFOLIO_SOURCE_TYPE,
        )
        action = "update" if existing is not None else "create"

        if dry_run:
            summary.files.append(
                PortfolioImportFilePlan(
                    source_path=source_path,
                    filename=filename,
                    title=title,
                    action=action,
                    existing_document_id=existing.id if existing else None,
                )
            )
            continue

        try:
            document, result_action, chunk_count = import_markdown_file(
                db,
                collection_id=collection.id,
                source_path=source_path,
                source_type=PORTFOLIO_SOURCE_TYPE,
                title=title,
            )
            summary.files.append(
                PortfolioImportFileResult(
                    filename=filename,
                    title=document.title,
                    action=result_action,
                    chunk_count=chunk_count,
                    embedding_status="embedded",
                    success=True,
                )
            )
        except Exception as exc:
            message = exc.message if hasattr(exc, "message") else str(exc)
            summary.files.append(
                PortfolioImportFileResult(
                    filename=filename,
                    title=title,
                    action=action,
                    embedding_status="failed",
                    success=False,
                    error=message,
                )
            )

    return summary
