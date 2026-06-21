from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Note
from app.schemas.note import NoteCreate, NoteRead, NoteUpdate
from app.services.classification_service import ClassificationService
from app.services.embedding_service import EmbeddingService

router = APIRouter(prefix="/notes", tags=["notes"])
embedding_service = EmbeddingService()
classification_service = ClassificationService()


@router.get("")
def list_notes(db: Session = Depends(get_db)) -> list[dict]:
    notes = db.scalars(select(Note).order_by(Note.created_at.desc())).all()
    return [NoteRead.model_validate(note).model_dump_camel() for note in notes]


@router.get("/{note_id}")
def get_note(note_id: str, db: Session = Depends(get_db)) -> dict:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteRead.model_validate(note).model_dump_camel()


@router.post("", status_code=201)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)) -> dict:
    category = payload.category
    confidence = None
    if not category or not category.strip():
        # Auto-classify empty categories
        res = classification_service.classify_text(payload.title, payload.content)
        category = res["category"]
        confidence = res["confidence"]

    note = Note(
        title=payload.title,
        content=payload.content,
        summary=payload.summary,
        category=category,
    )
    db.add(note)
    db.commit()
    db.refresh(note)

    # Index in Qdrant
    embedding_service.index_note(note.id, note.title, note.content)

    note_read = NoteRead.model_validate(note)
    note_read.category_confidence = confidence
    return note_read.model_dump_camel()


@router.put("/{note_id}")
def update_note(note_id: str, payload: NoteUpdate, db: Session = Depends(get_db)) -> dict:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    update_data = payload.model_dump(exclude_unset=True)
    category = update_data.get("category", note.category)
    confidence = None

    if not category or not category.strip():
        # Auto-classify when category is unset or explicitly cleared
        title = update_data.get("title", note.title)
        content = update_data.get("content", note.content)
        res = classification_service.classify_text(title, content)
        category = res["category"]
        confidence = res["confidence"]
        update_data["category"] = category

    for key, value in update_data.items():
        setattr(note, key, value)

    db.commit()
    db.refresh(note)

    # Re-index in Qdrant
    embedding_service.index_note(note.id, note.title, note.content)

    note_read = NoteRead.model_validate(note)
    note_read.category_confidence = confidence
    return note_read.model_dump_camel()


@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: str, db: Session = Depends(get_db)):
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()

    # Delete from Qdrant
    embedding_service.delete_note(note_id)

    return None
