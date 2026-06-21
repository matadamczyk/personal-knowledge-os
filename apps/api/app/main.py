import threading

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.api import chat, classify, ingest, notes, search
from app.core.database import Base, SessionLocal, engine
from app.models import Note
from app.services.embedding_service import EmbeddingService

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Personal Knowledge OS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173", "tauri://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(notes.router, prefix="/api")
app.include_router(ingest.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(classify.router, prefix="/api")
app.include_router(search.router, prefix="/api")


def startup_reindex():
    db = SessionLocal()
    try:
        es = EmbeddingService()
        if not es.is_active:
            return
        # Get all notes from SQLite
        notes_list = db.scalars(select(Note)).all()
        for note in notes_list:
            # Upsert note in Qdrant
            es.index_note(note.id, note.title, note.content)
    except Exception as e:
        print(f"Error during startup reindexing: {e}")
    finally:
        db.close()


@app.on_event("startup")
def startup_event() -> None:
    # Run in background thread to avoid blocking server start
    thread = threading.Thread(target=startup_reindex)
    thread.start()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
