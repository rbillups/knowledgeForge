from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    collection_id: int
    collection_name: str
    filename: str
    title: str
    file_type: str
    source_type: str
    status: str
    page_count: int | None
    chunk_count: int
    error_message: str | None
    created_at: datetime
    updated_at: datetime


class DocumentUploadResponse(BaseModel):
    id: int
    filename: str
    title: str
    file_type: str
    status: str
    chunk_count: int
    page_count: int | None = None
    message: str = Field(
        examples=["Document uploaded and indexed successfully."],
    )


class DocumentReindexResponse(BaseModel):
    id: int
    filename: str
    title: str
    status: str
    chunk_count: int
    message: str = Field(
        examples=["Document reindexed successfully."],
    )
