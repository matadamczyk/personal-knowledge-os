from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Note
from app.schemas.note import NoteCreate, NoteRead, NoteUpdate

router = APIRouter(prefix="/notes", tags=["notes"])


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
    note = Note(
        title=payload.title,
        content=payload.content,
        summary=payload.summary,
        category=payload.category,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return NoteRead.model_validate(note).model_dump_camel()


@router.put("/{note_id}")
def update_note(note_id: str, payload: NoteUpdate, db: Session = Depends(get_db)) -> dict:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(note, key, value)

    db.commit()
    db.refresh(note)
    return NoteRead.model_validate(note).model_dump_camel()


@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: str, db: Session = Depends(get_db)):
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()
    return None
