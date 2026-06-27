from fastapi.testclient import TestClient


def test_chat_rejects_empty_question(client: TestClient) -> None:
    response = client.post(
        "/api/v1/chat",
        json={
            "collection_id": 1,
            "question": "",
            "retrieval_limit": 5,
        },
    )

    assert response.status_code == 422


def test_chat_rejects_invalid_collection_id(client: TestClient) -> None:
    response = client.post(
        "/api/v1/chat",
        json={
            "collection_id": 0,
            "question": "What is our credential rotation policy?",
        },
    )

    assert response.status_code == 422


def test_chat_rejects_retrieval_limit_above_maximum(client: TestClient) -> None:
    response = client.post(
        "/api/v1/chat",
        json={
            "collection_id": 1,
            "question": "What is our credential rotation policy?",
            "retrieval_limit": 25,
        },
    )

    assert response.status_code == 422
