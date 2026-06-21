from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Note
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService

router = APIRouter(prefix="/chat", tags=["chat"])
embedding_service = EmbeddingService()
llm_service = LLMService()


class ChatRequest(BaseModel):
    message: str
    provider: str = "ollama"  # "ollama", "openai", "gemini"
    api_key: str | None = None
    model: str | None = None
    ollama_url: str | None = None


class SourceNote(BaseModel):
    id: str
    title: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceNote]


@router.post("", response_model=ChatResponse)
def chat_with_knowledge(payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    message_str = payload.message.strip()
    if not message_str:
        return ChatResponse(answer="Please enter a question.", sources=[])

    # 1. Retrieve matching note contexts from Qdrant
    hits = embedding_service.search_notes(message_str, limit=3)

    note_ids = [hit["id"] for hit in hits] if hits else []
    notes_map = {}
    if note_ids:
        notes = db.scalars(select(Note).where(Note.id.in_(note_ids))).all()
        notes_map = {note.id: note for note in notes}

    # 2. Build context
    context_items = []
    sources = []
    for hit in hits:
        note_id = hit["id"]
        note = notes_map.get(note_id)
        if note:
            context_items.append(f"--- Note: {note.title} ---\n{note.content}")
            sources.append(SourceNote(id=note.id, title=note.title, score=hit["score"]))

    # 3. Formulate RAG Prompt
    if context_items:
        context_str = "\n\n".join(context_items)
        prompt = (
            "You are a helpful personal second brain assistant. "
            "Use the retrieved notes context below to answer the user's question. "
            "Provide a direct, detailed, and structured answer. "
            "If the notes context does not contain the answer, "
            "state clearly that you don't know based on the notes, "
            "but list what relevant topics were found.\n\n"
            f"=== Context Notes ===\n{context_str}\n\n"
            f"=== User Question ===\n{message_str}\n\n"
            "=== Answer ==="
        )
    else:
        prompt = (
            "You are a helpful personal second brain assistant. "
            "The user asked: '{message_str}'. "
            "No matching notes were found in the knowledge base. "
            "Inform the user that no matching notes were found, "
            "and answer their question generally, clarifying that this "
            "is general knowledge and not based on their personal notes."
        )

    # 4. Generate LLM response
    answer = llm_service.generate_response(
        prompt=prompt,
        provider=payload.provider,
        api_key=payload.api_key,
        model=payload.model,
        ollama_url=payload.ollama_url,
    )

    # 5. Graceful Fallback if Ollama is offline/fails
    if answer is None:
        provider_name = "Ollama"
        if payload.provider == "openai":
            provider_name = "OpenAI"
        elif payload.provider == "gemini":
            provider_name = "Gemini"

        if sources:
            sources_summary = "\n".join([f"- **{src.title}**" for src in sources])
            answer = (
                f"⚠️ **LLM Provider ({provider_name}) is offline or unreachable.**\n\n"
                "I was unable to generate a conversational answer, but I "
                "found the following relevant notes in your database:\n\n"
                f"{sources_summary}\n\n"
                "Please verify your API key, model selection, or network connection settings."
            )
        else:
            answer = (
                f"⚠️ **LLM Provider ({provider_name}) is unreachable.**\n\n"
                "No matching notes were found, and the AI model is unreachable. "
                "Please check your settings and connection."
            )

    return ChatResponse(answer=answer, sources=sources)
