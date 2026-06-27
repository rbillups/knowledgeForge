from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.collection import CollectionResponse
from app.services.document_service import list_collections

router = APIRouter(prefix="/collections", tags=["Collections"])


@router.get(
    "",
    response_model=list[CollectionResponse],
    summary="List knowledge collections",
    description="Return all knowledge collections available for document uploads.",
)
def get_collections(db: Session = Depends(get_db)) -> list[CollectionResponse]:
    collections = list_collections(db)
    return [CollectionResponse.model_validate(item) for item in collections]
