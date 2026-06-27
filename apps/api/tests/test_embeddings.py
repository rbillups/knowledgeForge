from unittest.mock import MagicMock, patch

import pytest

from app.services.chunk_embedding_service import apply_embeddings_to_chunks
from app.services.embedding_service import EMBEDDING_DIMENSIONS, embed_texts
from app.services.exceptions import EmbeddingGenerationError, MissingApiKeyError


@patch("app.services.chunk_embedding_service.embed_texts")
def test_apply_embeddings_to_chunks_persists_vectors(
    mock_embed_texts: MagicMock,
) -> None:
    mock_embed_texts.return_value = [
        [0.1] * EMBEDDING_DIMENSIONS,
        [0.2] * EMBEDDING_DIMENSIONS,
    ]
    db = MagicMock()

    apply_embeddings_to_chunks(
        db,
        chunk_ids=[10, 11],
        chunk_texts=["first chunk", "second chunk"],
    )

    mock_embed_texts.assert_called_once_with(["first chunk", "second chunk"])
    assert db.execute.call_count == 2

    first_call = db.execute.call_args_list[0]
    assert first_call.args[1]["chunk_id"] == 10
    assert first_call.args[1]["embedding"].startswith("[")
    assert first_call.args[1]["embedding"].endswith("]")


@patch("app.services.embedding_service.settings.openai_api_key", None)
def test_embed_texts_requires_api_key() -> None:
    with pytest.raises(MissingApiKeyError):
        embed_texts(["sample text"])


@patch("app.services.embedding_service.OpenAI")
@patch("app.services.embedding_service.settings.openai_api_key", "test-key")
@patch(
    "app.services.embedding_service.settings.embedding_model",
    "text-embedding-3-small",
)
def test_embed_texts_raises_safe_error_on_openai_failure(
    mock_openai: MagicMock,
) -> None:
    mock_openai.return_value.embeddings.create.side_effect = RuntimeError(
        "provider failure"
    )

    with pytest.raises(EmbeddingGenerationError) as exc_info:
        embed_texts(["sample text"])

    assert exc_info.value.message == "Unable to generate embeddings at this time."
