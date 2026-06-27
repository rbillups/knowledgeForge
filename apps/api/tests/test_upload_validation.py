from fastapi.testclient import TestClient


def test_upload_rejects_unsupported_file_type(client: TestClient) -> None:
    response = client.post(
        "/api/v1/documents/upload",
        data={"collection_id": "1"},
        files={
            "file": (
                "report.docx",
                b"fake docx content",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Unsupported file type. Allowed types: PDF, TXT, and Markdown."
    )


def test_upload_rejects_empty_file(client: TestClient) -> None:
    response = client.post(
        "/api/v1/documents/upload",
        data={"collection_id": "1"},
        files={"file": ("notes.txt", b"", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Uploaded files cannot be empty."
