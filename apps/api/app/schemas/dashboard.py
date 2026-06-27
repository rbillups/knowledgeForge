from datetime import datetime

from pydantic import BaseModel, Field


class DashboardRecentDocument(BaseModel):
    title: str = Field(
        description="Document title stored in the knowledge base.",
        examples=["Projects"],
    )
    filename: str = Field(
        description="Original filename of the document.",
        examples=["03_projects.md"],
    )
    collection_name: str = Field(
        description="Name of the knowledge collection containing the document.",
        examples=["Portfolio Knowledge Base"],
    )
    status: str = Field(
        description="Current indexing status of the document.",
        examples=["indexed"],
    )
    chunk_count: int = Field(
        description="Number of indexed chunks for the document.",
        examples=[4],
    )
    updated_at: datetime = Field(
        description="Most recent document update timestamp.",
    )


class DashboardCollectionSummary(BaseModel):
    id: int = Field(
        description="Knowledge collection identifier.",
        examples=[1],
    )
    slug: str = Field(
        description="URL-safe collection slug.",
        examples=["portfolio"],
    )
    name: str = Field(
        description="Display name of the knowledge collection.",
        examples=["Portfolio Knowledge Base"],
    )
    document_count: int = Field(
        description="Total documents in the collection.",
        examples=[7],
    )
    indexed_document_count: int = Field(
        description="Documents with indexed status in the collection.",
        examples=[7],
    )
    chunk_count: int = Field(
        description="Total indexed chunks across documents in the collection.",
        examples=[28],
    )


class DashboardSummaryResponse(BaseModel):
    total_collections: int = Field(
        description="Total number of knowledge collections.",
        examples=[1],
    )
    total_documents: int = Field(
        description="Total number of documents across all collections.",
        examples=[7],
    )
    total_indexed_documents: int = Field(
        description="Documents with indexed status.",
        examples=[7],
    )
    total_processing_documents: int = Field(
        description="Documents currently uploaded or processing.",
        examples=[0],
    )
    total_failed_documents: int = Field(
        description="Documents that failed indexing.",
        examples=[0],
    )
    total_chunks: int = Field(
        description="Total indexed chunks across all documents.",
        examples=[28],
    )
    recent_documents: list[DashboardRecentDocument] = Field(
        description="Up to five most recently updated documents.",
    )
    collections: list[DashboardCollectionSummary] = Field(
        description="Operational summary for each knowledge collection.",
    )
    api_status: str = Field(
        description="API availability status for this summary request.",
        examples=["ok"],
    )
    database_status: str = Field(
        description="Database connectivity status.",
        examples=["ok"],
    )
