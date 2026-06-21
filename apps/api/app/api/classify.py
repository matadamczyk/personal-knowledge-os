from fastapi import APIRouter
from pydantic import BaseModel

from app.services.classification_service import ClassificationService

router = APIRouter(prefix="/classify", tags=["classify"])
classification_service = ClassificationService()


class ClassifyRequest(BaseModel):
    title: str
    content: str = ""


class ClassifyResponse(BaseModel):
    category: str
    confidence: float


@router.post("", response_model=ClassifyResponse)
def classify_note(payload: ClassifyRequest) -> ClassifyResponse:
    res = classification_service.classify_text(payload.title, payload.content)
    return ClassifyResponse(
        category=res["category"],
        confidence=res["confidence"],
    )
