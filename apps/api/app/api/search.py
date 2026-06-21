from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Note
from app.services.embedding_service import EmbeddingService

router = APIRouter(prefix="/search", tags=["search"])
embedding_service = EmbeddingService()


class SearchRequest(BaseModel):
    query: str
    limit: int = 5


@router.post("")
def search(payload: SearchRequest, db: Session = Depends(get_db)) -> list[dict]:
    query_str = payload.query.strip()
    if not query_str:
        return []

    # Get search matches from Qdrant
    hits = embedding_service.search_notes(query_str, limit=payload.limit)
    if not hits:
        return []

    # Map hits by ID to fetch them from database in bulk
    note_ids = [hit["id"] for hit in hits]
    notes = db.scalars(select(Note).where(Note.id.in_(note_ids))).all()
    notes_map = {note.id: note for note in notes}

    results = []
    for hit in hits:
        note_id = hit["id"]
        note = notes_map.get(note_id)
        if note:
            # Generate excerpt from content
            excerpt = note.content[:200]
            if len(note.content) > 200:
                excerpt += "..."
            results.append(
                {
                    "id": note.id,
                    "score": hit["score"],
                    "title": note.title,
                    "excerpt": excerpt,
                }
            )

    return results
