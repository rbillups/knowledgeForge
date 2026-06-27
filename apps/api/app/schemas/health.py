from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(examples=["ok"])
    service: str = Field(examples=["knowledgeforge-api"])


class ReadinessResponse(BaseModel):
    ready: bool = Field(
        description="Whether the API is ready to serve traffic.",
        examples=[True],
    )
    environment: str = Field(
        description="Configured application environment.",
        examples=["development"],
    )
    storage_provider: str = Field(
        description="Configured storage provider.",
        examples=["local"],
    )
    database_status: str = Field(
        description="Database connectivity status.",
        examples=["ok"],
    )
    storage_status: str = Field(
        description="Storage connectivity status.",
        examples=["ok"],
    )
