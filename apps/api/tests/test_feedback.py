from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.schemas.feedback import FeedbackCreateRequest, FeedbackCreateResponse
from app.services.exceptions import CollectionNotFoundError
from app.services.feedback_service import (
    create_feedback,
    get_feedback_summary,
    resolve_feedback_document_id,
)


def test_resolve_feedback_document_id_uses_first_valid_citation_id() -> None:
    db = MagicMock()
    document = MagicMock()
    document.id = 12
    db.scalar.return_value = document

    document_id = resolve_feedback_document_id(
        db,
        collection_id=1,
        citation_document_ids=[99, 12],
        citation_filenames=None,
    )

    assert document_id == 12


def test_resolve_feedback_document_id_falls_back_to_filename() -> None:
    db = MagicMock()
    document = MagicMock()
    document.id = 7
    db.scalar.side_effect = [None, document]

    document_id = resolve_feedback_document_id(
        db,
        collection_id=1,
        citation_document_ids=[404],
        citation_filenames=["03_projects.md"],
    )

    assert document_id == 7


@patch("app.services.feedback_service.resolve_feedback_document_id")
def test_create_feedback_stores_anonymous_rating(
    mock_resolve_document: MagicMock,
) -> None:
    mock_resolve_document.return_value = 3
    db = MagicMock()
    db.get.return_value = MagicMock(id=1)

    response = create_feedback(
        db,
        FeedbackCreateRequest(
            collection_id=1,
            question="What is KnowledgeForge?",
            answer="KnowledgeForge is a citation-grounded AI platform.",
            feedback_type="helpful",
            comment=None,
            citation_filenames=["03_projects.md"],
        ),
    )

    assert response == FeedbackCreateResponse(
        message="Feedback recorded successfully.",
    )
    db.add.assert_called_once()
    feedback = db.add.call_args[0][0]
    assert feedback.rating == "helpful"
    assert feedback.question == "What is KnowledgeForge?"
    assert feedback.document_id == 3
    assert feedback.notes is None
    db.commit.assert_called_once()


def test_create_feedback_raises_for_missing_collection() -> None:
    db = MagicMock()
    db.get.return_value = None

    try:
        create_feedback(
            db,
            FeedbackCreateRequest(
                collection_id=404,
                question="Question?",
                answer="Answer.",
                feedback_type="not_helpful",
            ),
        )
    except CollectionNotFoundError as exc:
        assert exc.collection_id == 404
    else:
        raise AssertionError("Expected CollectionNotFoundError")


def test_get_feedback_summary_returns_counts_and_recent_entries() -> None:
    created_at = datetime(2026, 6, 26, 12, 0, tzinfo=timezone.utc)
    recent = MagicMock()
    recent.question = "What is KnowledgeForge?"
    recent.rating = "helpful"
    recent.created_at = created_at

    db = MagicMock()
    db.scalar.side_effect = [3, 2, 1]
    db.scalars.return_value.all.return_value = [recent]

    summary = get_feedback_summary(db)

    assert summary.total_feedback == 3
    assert summary.helpful_count == 2
    assert summary.not_helpful_count == 1
    assert summary.helpful_percentage == 66.7
    assert len(summary.recent_feedback) == 1
    assert summary.recent_feedback[0].feedback_type == "helpful"


def test_get_feedback_summary_returns_empty_state() -> None:
    db = MagicMock()
    db.scalar.side_effect = [0, 0, 0]
    db.scalars.return_value.all.return_value = []

    summary = get_feedback_summary(db)

    assert summary.total_feedback == 0
    assert summary.helpful_percentage is None
    assert summary.recent_feedback == []


@patch("app.api.routes.feedback.create_feedback")
def test_submit_feedback_endpoint_returns_created(
    mock_create_feedback: MagicMock,
    client: TestClient,
) -> None:
    mock_create_feedback.return_value = FeedbackCreateResponse(
        message="Feedback recorded successfully.",
    )

    response = client.post(
        "/api/v1/feedback",
        json={
            "collection_id": 1,
            "question": "What is KnowledgeForge?",
            "answer": "KnowledgeForge is a citation-grounded AI platform.",
            "feedback_type": "helpful",
            "citation_filenames": ["03_projects.md"],
        },
    )

    assert response.status_code == 201
    assert response.json()["message"] == "Feedback recorded successfully."


@patch("app.api.routes.feedback.create_feedback")
def test_submit_feedback_endpoint_returns_not_found_for_missing_collection(
    mock_create_feedback: MagicMock,
    client: TestClient,
) -> None:
    mock_create_feedback.side_effect = CollectionNotFoundError(99)

    response = client.post(
        "/api/v1/feedback",
        json={
            "collection_id": 99,
            "question": "Question?",
            "answer": "Answer.",
            "feedback_type": "helpful",
        },
    )

    assert response.status_code == 404


def test_submit_feedback_rejects_empty_question(client: TestClient) -> None:
    response = client.post(
        "/api/v1/feedback",
        json={
            "collection_id": 1,
            "question": "   ",
            "answer": "Answer.",
            "feedback_type": "helpful",
        },
    )

    assert response.status_code == 422


def test_submit_feedback_rejects_invalid_feedback_type(client: TestClient) -> None:
    response = client.post(
        "/api/v1/feedback",
        json={
            "collection_id": 1,
            "question": "Question?",
            "answer": "Answer.",
            "feedback_type": "mixed",
        },
    )

    assert response.status_code == 422


def test_submit_feedback_rejects_overlong_comment(client: TestClient) -> None:
    response = client.post(
        "/api/v1/feedback",
        json={
            "collection_id": 1,
            "question": "Question?",
            "answer": "Answer.",
            "feedback_type": "not_helpful",
            "comment": "x" * 501,
        },
    )

    assert response.status_code == 422


@patch("app.api.routes.feedback.get_feedback_summary")
def test_feedback_summary_endpoint_returns_summary(
    mock_get_feedback_summary: MagicMock,
    client: TestClient,
) -> None:
    from app.schemas.feedback import FeedbackRecentEntry, FeedbackSummaryResponse

    created_at = datetime(2026, 6, 26, 12, 0, tzinfo=timezone.utc)
    mock_get_feedback_summary.return_value = FeedbackSummaryResponse(
        total_feedback=2,
        helpful_count=1,
        not_helpful_count=1,
        helpful_percentage=50.0,
        recent_feedback=[
            FeedbackRecentEntry(
                question_preview="What is KnowledgeForge?",
                feedback_type="helpful",
                created_at=created_at,
            )
        ],
    )

    response = client.get("/api/v1/feedback/summary")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_feedback"] == 2
    assert payload["helpful_percentage"] == 50.0
    assert payload["recent_feedback"][0]["feedback_type"] == "helpful"
