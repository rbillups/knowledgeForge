from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class FeedbackCreateRequest(BaseModel):
    collection_id: int = Field(
        ...,
        gt=0,
        description="Knowledge collection the answered question was asked against.",
    )
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Original user question.",
    )
    answer: str = Field(
        ...,
        min_length=1,
        max_length=8000,
        description="Assistant answer being rated.",
    )
    feedback_type: Literal["helpful", "not_helpful"] = Field(
        description="Whether the answer was helpful.",
    )
    comment: str | None = Field(
        default=None,
        max_length=500,
        description="Optional short comment, typically for not-helpful feedback.",
    )
    citation_document_ids: list[int] | None = Field(
        default=None,
        description="Optional cited document identifiers from the answer.",
    )
    citation_filenames: list[str] | None = Field(
        default=None,
        description="Optional cited document filenames from the answer.",
    )

    @field_validator("question", "answer")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("must not be empty.")
        return stripped

    @field_validator("comment")
    @classmethod
    def strip_optional_comment(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class FeedbackCreateResponse(BaseModel):
    message: str = Field(
        examples=["Feedback recorded successfully."],
    )


class FeedbackRecentEntry(BaseModel):
    question_preview: str = Field(
        description="Short preview of the rated question.",
    )
    feedback_type: Literal["helpful", "not_helpful"]
    created_at: datetime


class FeedbackSummaryResponse(BaseModel):
    total_feedback: int = Field(
        description="Total number of feedback entries recorded.",
        examples=[12],
    )
    helpful_count: int = Field(
        description="Number of helpful ratings.",
        examples=[9],
    )
    not_helpful_count: int = Field(
        description="Number of not helpful ratings.",
        examples=[3],
    )
    helpful_percentage: float | None = Field(
        description="Share of helpful ratings when feedback exists.",
        examples=[75.0],
    )
    recent_feedback: list[FeedbackRecentEntry] = Field(
        description="Up to five most recent feedback entries.",
    )
