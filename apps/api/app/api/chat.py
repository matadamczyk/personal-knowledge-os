from fastapi import APIRouter

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("")
def chat() -> dict[str, str]:
    return {"status": "not_implemented"}
