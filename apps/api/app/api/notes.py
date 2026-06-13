from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Note
from app.schemas.note import NoteCreate, NoteRead

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("")
def list_notes(db: Session = Depends(get_db)) -> list[dict]:
    notes = db.scalars(select(Note).order_by(Note.created_at.desc())).all()
    return [NoteRead.model_validate(note).model_dump_camel() for note in notes]


@router.post("", status_code=201)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)) -> dict:
    note = Note(title=payload.title, content=payload.content)
    db.add(note)
    db.commit()
    db.refresh(note)
    return NoteRead.model_validate(note).model_dump_camel()
