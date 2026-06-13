from app.core.config import settings


class EmbeddingService:
    def __init__(self) -> None:
        self.collection = settings.qdrant_collection

    def embed_text(self, text: str) -> list[float]:
        # Placeholder for sentence-transformers integration after note CRUD is stable.
        return [0.0]
