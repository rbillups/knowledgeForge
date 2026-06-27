from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CollectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime
