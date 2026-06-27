import logging

from openai import OpenAI
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.schemas.chat import ChatCitation, ChatRequest, ChatResponse
from app.schemas.search import SearchRequest, SearchResultItem
from app.services.exceptions import ChatGenerationError, MissingApiKeyError
from app.services.privacy_policy_service import (
    PRIVACY_BLOCKED_ANSWER,
    is_privacy_sensitive_question,
)
from app.services.search_service import semantic_search

logger = logging.getLogger(__name__)

INSUFFICIENT_ANSWER = (
    "I do not have enough information in this knowledge base to answer that."
)

SYSTEM_INSTRUCTIONS = """You are a knowledge assistant for an enterprise document library.
Answer only from the retrieved source context provided in the user message.
Do not use outside knowledge.
Do not invent experience, dates, skills, or facts.
If the sources do not support an answer, respond exactly with:
"I do not have enough information in this knowledge base to answer that."
Keep responses concise and professional."""


def grounded_chat(db: Session, request: ChatRequest) -> ChatResponse:
    if is_privacy_sensitive_question(request.question):
        logger.info(
            "Blocked privacy-sensitive chat request for collection %s",
            request.collection_id,
        )
        return ChatResponse(
            answer=PRIVACY_BLOCKED_ANSWER,
            citations=[],
            insufficient_context=True,
            policy_blocked=True,
            model=None,
        )

    search_response = semantic_search(
        db,
        SearchRequest(
            collection_id=request.collection_id,
            query=request.question,
            limit=request.retrieval_limit,
        ),
    )

    citations = [_to_citation(item) for item in search_response.results]

    if not search_response.results:
        logger.info(
            "Grounded chat found no source chunks for collection %s",
            request.collection_id,
        )
        return ChatResponse(
            answer=INSUFFICIENT_ANSWER,
            citations=[],
            insufficient_context=True,
            policy_blocked=False,
            model=settings.chat_model,
        )

    answer = generate_grounded_answer(
        question=request.question.strip(),
        context_chunks=search_response.results,
    )
    insufficient_context = _is_insufficient_answer(answer)

    logger.info(
        "Grounded chat completed for collection %s using %s chunk(s), "
        "insufficient_context=%s, question_length=%s",
        request.collection_id,
        len(citations),
        insufficient_context,
        len(request.question.strip()),
    )

    return ChatResponse(
        answer=answer,
        citations=citations,
        insufficient_context=insufficient_context,
        policy_blocked=False,
        model=settings.chat_model,
    )


def generate_grounded_answer(
    *,
    question: str,
    context_chunks: list[SearchResultItem],
) -> str:
    if not settings.openai_api_key:
        raise MissingApiKeyError()

    context_block = _format_context(context_chunks)
    user_input = (
        f"Question:\n{question}\n\n"
        f"Retrieved source context:\n{context_block}"
    )

    try:
        client = OpenAI(api_key=settings.openai_api_key)
        response = client.responses.create(
            model=settings.chat_model,
            instructions=SYSTEM_INSTRUCTIONS,
            input=user_input,
        )
    except MissingApiKeyError:
        raise
    except Exception as exc:
        logger.exception(
            "Chat generation failed using model %s",
            settings.chat_model,
        )
        raise ChatGenerationError(
            "Unable to generate a chat response at this time."
        ) from exc

    answer = response.output_text.strip()
    if not answer:
        raise ChatGenerationError(
            "Unable to generate a chat response at this time."
        )

    return answer


def _format_context(context_chunks: list[SearchResultItem]) -> str:
    sections: list[str] = []
    for index, chunk in enumerate(context_chunks, start=1):
        page_label = (
            f"Page {chunk.page_number}"
            if chunk.page_number is not None
            else "Page unknown"
        )
        sections.append(
            "\n".join(
                [
                    f"[Source {index}]",
                    f"Title: {chunk.document_title}",
                    f"Filename: {chunk.filename}",
                    f"Chunk index: {chunk.chunk_index}",
                    page_label,
                    "Content:",
                    chunk.chunk_content,
                ]
            )
        )
    return "\n\n".join(sections)


def _to_citation(item: SearchResultItem) -> ChatCitation:
    return ChatCitation(
        document_title=item.document_title,
        filename=item.filename,
        chunk_content=item.chunk_content,
        chunk_index=item.chunk_index,
        page_number=item.page_number,
        similarity_score=item.similarity_score,
    )


def _is_insufficient_answer(answer: str) -> bool:
    normalized = answer.strip().lower()
    return normalized == INSUFFICIENT_ANSWER.lower()
