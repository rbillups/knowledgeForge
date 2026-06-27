import logging

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.knowledge_collection import KnowledgeCollection
from app.schemas.search import SearchRequest, SearchResponse, SearchResultItem
from app.services.embedding_service import embed_texts, vector_to_literal
from app.services.exceptions import CollectionNotFoundError

logger = logging.getLogger(__name__)


def semantic_search(db: Session, request: SearchRequest) -> SearchResponse:
    collection = db.get(KnowledgeCollection, request.collection_id)
    if collection is None:
        raise CollectionNotFoundError(request.collection_id)

    query_embedding = embed_texts([request.query.strip()])[0]
    query_literal = vector_to_literal(query_embedding)

    rows = db.execute(
        text(
            """
            SELECT
                d.title AS document_title,
                d.filename,
                dc.content AS chunk_content,
                dc.chunk_index,
                dc.page_number,
                1 - (dc.embedding <=> CAST(:query_embedding AS vector)) AS similarity_score
            FROM document_chunks dc
            INNER JOIN documents d ON d.id = dc.document_id
            WHERE d.collection_id = :collection_id
              AND d.status = 'indexed'
              AND dc.embedding IS NOT NULL
            ORDER BY dc.embedding <=> CAST(:query_embedding AS vector)
            LIMIT :limit
            """
        ),
        {
            "query_embedding": query_literal,
            "collection_id": request.collection_id,
            "limit": request.limit,
        },
    ).mappings()

    results = [
        SearchResultItem(
            document_title=row["document_title"],
            filename=row["filename"],
            chunk_content=row["chunk_content"],
            chunk_index=row["chunk_index"],
            page_number=row["page_number"],
            similarity_score=round(float(row["similarity_score"]), 6),
        )
        for row in rows
    ]

    logger.info(
        "Semantic search returned %s result(s) for collection %s",
        len(results),
        request.collection_id,
    )

    return SearchResponse(
        collection_id=request.collection_id,
        query=request.query.strip(),
        limit=request.limit,
        results=results,
    )
