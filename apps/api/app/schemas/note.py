from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=240)
    content: str = ""
    summary: str | None = None
    category: str | None = None


class NoteUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=240)
    content: str | None = None
    summary: str | None = None
    category: str | None = None


class NoteRead(BaseModel):
    id: str
    title: str
    content: str
    summary: str | None = None
    category: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    def model_dump_camel(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "summary": self.summary,
            "category": self.category,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
        }
