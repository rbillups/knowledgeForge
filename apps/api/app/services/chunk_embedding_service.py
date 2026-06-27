from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.embedding_service import embed_texts, vector_to_literal


def apply_embeddings_to_chunks(
    db: Session,
    *,
    chunk_ids: list[int],
    chunk_texts: list[str],
) -> None:
    if len(chunk_ids) != len(chunk_texts):
        raise ValueError("Chunk IDs and chunk texts must have the same length.")

    embeddings = embed_texts(chunk_texts)

    if len(embeddings) != len(chunk_ids):
        raise ValueError("Embedding count does not match chunk count.")

    for chunk_id, embedding in zip(chunk_ids, embeddings, strict=True):
        db.execute(
            text(
                "UPDATE document_chunks "
                "SET embedding = CAST(:embedding AS vector) "
                "WHERE id = :chunk_id"
            ),
            {
                "embedding": vector_to_literal(embedding),
                "chunk_id": chunk_id,
            },
        )
