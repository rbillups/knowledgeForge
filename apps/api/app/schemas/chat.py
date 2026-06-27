from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    collection_id: int = Field(
        ...,
        gt=0,
        description="Knowledge collection to answer from.",
    )
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User question to answer using retrieved source chunks.",
        examples=["What is our API credential rotation policy?"],
    )
    retrieval_limit: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of source chunks to retrieve for grounding.",
    )


class ChatCitation(BaseModel):
    document_title: str
    filename: str
    chunk_content: str
    chunk_index: int
    page_number: int | None
    similarity_score: float = Field(
        description="Cosine similarity score between the question and chunk.",
    )


class ChatResponse(BaseModel):
    answer: str
    citations: list[ChatCitation]
    insufficient_context: bool = Field(
        description=(
            "True when the knowledge base does not contain enough "
            "supporting information to answer the question."
        ),
    )
    policy_blocked: bool = Field(
        default=False,
        description=(
            "True when the request was blocked by a privacy or safety policy "
            "before retrieval or model generation."
        ),
    )
    model: str | None = Field(
        default=None,
        description="Chat model used to generate the answer, if applicable.",
    )
