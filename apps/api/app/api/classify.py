from fastapi import APIRouter

router = APIRouter(prefix="/classify", tags=["classify"])


@router.post("")
def classify() -> dict[str, str]:
    return {"status": "not_implemented"}
