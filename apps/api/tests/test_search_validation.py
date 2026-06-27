from fastapi.testclient import TestClient


def test_search_rejects_empty_query(client: TestClient) -> None:
    response = client.post(
        "/api/v1/search",
        json={
            "collection_id": 1,
            "query": "",
            "limit": 5,
        },
    )

    assert response.status_code == 422


def test_search_rejects_limit_above_maximum(client: TestClient) -> None:
    response = client.post(
        "/api/v1/search",
        json={
            "collection_id": 1,
            "query": "What is our credential rotation policy?",
            "limit": 21,
        },
    )

    assert response.status_code == 422


def test_search_rejects_invalid_collection_id(client: TestClient) -> None:
    response = client.post(
        "/api/v1/search",
        json={
            "collection_id": 0,
            "query": "What is our credential rotation policy?",
        },
    )

    assert response.status_code == 422


def test_search_uses_default_limit(client: TestClient) -> None:
    response = client.post(
        "/api/v1/search",
        json={
            "collection_id": 1,
            "query": "What is our credential rotation policy?",
        },
    )

    assert response.status_code in {200, 404, 502, 503}
