from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.schemas.dashboard import (
    DashboardCollectionSummary,
    DashboardRecentDocument,
    DashboardSummaryResponse,
)
from app.services.dashboard_service import check_database_status, get_dashboard_summary


def test_check_database_status_returns_ok_when_query_succeeds() -> None:
    db = MagicMock()

    assert check_database_status(db) == "ok"
    db.execute.assert_called_once()


def test_check_database_status_returns_unavailable_on_failure() -> None:
    db = MagicMock()
    db.execute.side_effect = RuntimeError("connection refused")

    assert check_database_status(db) == "unavailable"


@patch("app.services.dashboard_service.check_database_status")
def test_get_dashboard_summary_returns_aggregated_metrics(
    mock_check_database_status: MagicMock,
) -> None:
    mock_check_database_status.return_value = "ok"
    updated_at = datetime(2026, 6, 26, 12, 0, tzinfo=timezone.utc)

    db = MagicMock()
    db.scalar.side_effect = [1, 7, 6, 1, 0, 42]
    recent_result = MagicMock()
    recent_result.all.return_value = [
        (
            "Projects",
            "03_projects.md",
            "indexed",
            4,
            updated_at,
            "Portfolio Knowledge Base",
        )
    ]
    collection_result = MagicMock()
    collection_result.all.return_value = [
        (1, "portfolio", "Portfolio Knowledge Base", 7, 6, 42),
    ]
    db.execute.side_effect = [recent_result, collection_result]

    summary = get_dashboard_summary(db)

    assert summary.total_collections == 1
    assert summary.total_documents == 7
    assert summary.total_indexed_documents == 6
    assert summary.total_processing_documents == 1
    assert summary.total_failed_documents == 0
    assert summary.total_chunks == 42
    assert summary.api_status == "ok"
    assert summary.database_status == "ok"
    assert len(summary.recent_documents) == 1
    assert summary.recent_documents[0].filename == "03_projects.md"
    assert len(summary.collections) == 1
    assert summary.collections[0].slug == "portfolio"
    assert summary.collections[0].indexed_document_count == 6


@patch("app.api.routes.dashboard.get_dashboard_summary")
def test_dashboard_summary_endpoint_returns_summary(
    mock_get_dashboard_summary: MagicMock,
    client: TestClient,
) -> None:
    updated_at = datetime(2026, 6, 26, 12, 0, tzinfo=timezone.utc)
    mock_get_dashboard_summary.return_value = DashboardSummaryResponse(
        total_collections=1,
        total_documents=2,
        total_indexed_documents=2,
        total_processing_documents=0,
        total_failed_documents=0,
        total_chunks=8,
        recent_documents=[
            DashboardRecentDocument(
                title="About",
                filename="01_about.md",
                collection_name="Portfolio Knowledge Base",
                status="indexed",
                chunk_count=2,
                updated_at=updated_at,
            )
        ],
        collections=[
            DashboardCollectionSummary(
                id=1,
                slug="portfolio",
                name="Portfolio Knowledge Base",
                document_count=2,
                indexed_document_count=2,
                chunk_count=8,
            )
        ],
        api_status="ok",
        database_status="ok",
    )

    response = client.get("/api/v1/dashboard/summary")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_collections"] == 1
    assert payload["total_indexed_documents"] == 2
    assert payload["total_chunks"] == 8
    assert payload["database_status"] == "ok"
    assert payload["recent_documents"][0]["filename"] == "01_about.md"


@patch("app.api.routes.dashboard.get_dashboard_summary")
def test_dashboard_summary_endpoint_returns_service_unavailable_on_db_error(
    mock_get_dashboard_summary: MagicMock,
    client: TestClient,
) -> None:
    from sqlalchemy.exc import SQLAlchemyError

    mock_get_dashboard_summary.side_effect = SQLAlchemyError("database unavailable")

    response = client.get("/api/v1/dashboard/summary")

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Unable to load dashboard summary at this time."
    )
