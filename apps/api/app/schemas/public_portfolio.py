from pydantic import BaseModel, Field


class PublicPortfolioChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Question about Key'Shawn Billups' public portfolio materials.",
        examples=["What is KnowledgeForge?"],
    )
    retrieval_limit: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of portfolio source chunks to retrieve.",
    )
