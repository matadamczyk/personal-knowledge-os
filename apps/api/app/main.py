from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat, classify, ingest, notes
from app.core.database import Base, engine

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


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
