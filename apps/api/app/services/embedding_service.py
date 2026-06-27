import logging

from openai import OpenAI

from app.config.settings import settings
from app.services.exceptions import EmbeddingGenerationError, MissingApiKeyError

logger = logging.getLogger(__name__)

EMBEDDING_DIMENSIONS = 1536


def vector_to_literal(values: list[float]) -> str:
    return "[" + ",".join(str(float(value)) for value in values) + "]"


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    if not settings.openai_api_key:
        raise MissingApiKeyError()

    try:
        client = OpenAI(api_key=settings.openai_api_key)
        response = client.embeddings.create(
            input=texts,
            model=settings.embedding_model,
        )
    except MissingApiKeyError:
        raise
    except Exception as exc:
        logger.exception(
            "Embedding generation failed for %s text(s) using model %s",
            len(texts),
            settings.embedding_model,
        )
        raise EmbeddingGenerationError(
            "Unable to generate embeddings at this time."
        ) from exc

    ordered_embeddings = sorted(response.data, key=lambda item: item.index)
    embeddings = [item.embedding for item in ordered_embeddings]

    for embedding in embeddings:
        if len(embedding) != EMBEDDING_DIMENSIONS:
            logger.error(
                "Unexpected embedding dimension %s from model %s",
                len(embedding),
                settings.embedding_model,
            )
            raise EmbeddingGenerationError(
                "Unable to generate embeddings at this time."
            )

    return embeddings
