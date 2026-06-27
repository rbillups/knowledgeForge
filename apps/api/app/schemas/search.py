from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    collection_id: int = Field(
        ...,
        gt=0,
        description="Knowledge collection to search within.",
    )
    query: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Natural-language question or search phrase.",
        examples=["What is our API credential rotation policy?"],
    )
    limit: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of matching chunks to return.",
    )


class SearchResultItem(BaseModel):
    document_title: str
    filename: str
    chunk_content: str
    chunk_index: int
    page_number: int | None
    similarity_score: float = Field(
        description="Cosine similarity score between 0 and 1.",
    )


class SearchResponse(BaseModel):
    collection_id: int
    query: str
    limit: int
    results: list[SearchResultItem]
