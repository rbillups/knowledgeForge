from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.services.document_service import find_document_in_collection
from app.services.portfolio_import_service import (
    PORTFOLIO_SOURCE_TYPE,
    PortfolioImportFilePlan,
    PortfolioImportFileResult,
    discover_portfolio_source_files,
    import_portfolio_pack,
    readable_title_for_filename,
    resolve_portfolio_source_dir,
)


def test_discover_portfolio_source_files_finds_markdown_files(
    tmp_path: Path,
) -> None:
    (tmp_path / "01_about.md").write_text("# About", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("ignore", encoding="utf-8")
    (tmp_path / "02_experience.md").write_text("# Experience", encoding="utf-8")

    files = discover_portfolio_source_files(tmp_path)

    assert [path.name for path in files] == ["01_about.md", "02_experience.md"]


def test_readable_title_for_filename_uses_mapping() -> None:
    assert readable_title_for_filename("03_projects.md") == "Projects"


def test_resolve_portfolio_source_dir_uses_custom_path(tmp_path: Path) -> None:
    custom_dir = tmp_path / "portfolio-source"
    custom_dir.mkdir()

    assert resolve_portfolio_source_dir(custom_dir) == custom_dir.resolve()


@patch("app.services.document_service.find_document_in_collection")
@patch("app.services.document_service.get_collection_by_slug")
def test_import_portfolio_pack_dry_run_lists_planned_actions(
    mock_get_collection: MagicMock,
    mock_find_document: MagicMock,
    tmp_path: Path,
) -> None:
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "01_about.md").write_text("# About", encoding="utf-8")

    mock_collection = MagicMock()
    mock_collection.id = 1
    mock_get_collection.return_value = mock_collection
    mock_find_document.return_value = None

    db = MagicMock()
    summary = import_portfolio_pack(db, source_dir=source_dir, dry_run=True)

    assert summary.dry_run is True
    assert len(summary.files) == 1
    plan = summary.files[0]
    assert isinstance(plan, PortfolioImportFilePlan)
    assert plan.filename == "01_about.md"
    assert plan.title == "About"
    assert plan.action == "create"
    db.commit.assert_not_called()


@patch("app.services.document_service.import_markdown_file")
@patch("app.services.document_service.find_document_in_collection")
@patch("app.services.document_service.get_collection_by_slug")
def test_import_portfolio_pack_updates_existing_document_by_filename(
    mock_get_collection: MagicMock,
    mock_find_document: MagicMock,
    mock_import_markdown_file: MagicMock,
    tmp_path: Path,
) -> None:
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    source_file = source_dir / "02_experience.md"
    source_file.write_text("# Experience", encoding="utf-8")

    mock_collection = MagicMock()
    mock_collection.id = 1
    mock_get_collection.return_value = mock_collection

    existing_document = MagicMock()
    existing_document.id = 42
    mock_find_document.return_value = existing_document

    updated_document = MagicMock()
    updated_document.title = "Professional Experience"
    updated_document.chunk_count = 3
    mock_import_markdown_file.return_value = (updated_document, "updated", 3)

    db = MagicMock()
    summary = import_portfolio_pack(db, source_dir=source_dir, dry_run=False)

    assert summary.failed == 0
    result = summary.files[0]
    assert isinstance(result, PortfolioImportFileResult)
    assert result.action == "updated"
    assert result.chunk_count == 3
    assert result.embedding_status == "embedded"

    mock_import_markdown_file.assert_called_once_with(
        db,
        collection_id=1,
        source_path=source_file,
        source_type=PORTFOLIO_SOURCE_TYPE,
        title="Professional Experience",
    )


def test_find_document_in_collection_filters_by_source_type() -> None:
    db = MagicMock()
    db.scalar.return_value = MagicMock(id=7)

    document = find_document_in_collection(
        db,
        collection_id=1,
        filename="01_about.md",
        source_type="portfolio",
    )

    assert document is not None
    assert document.id == 7
