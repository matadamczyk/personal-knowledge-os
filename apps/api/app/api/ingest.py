from fastapi import APIRouter

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("")
def ingest_document() -> dict[str, str]:
    return {"status": "not_implemented"}
