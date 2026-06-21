import logging

from app.core.config import settings
from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointIdsList, PointStruct, VectorParams

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self) -> None:
        self.collection = settings.qdrant_collection
        try:
            self.client = QdrantClient(url=settings.qdrant_url)
            self.model = TextEmbedding()  # Default: BAAI/bge-small-en-v1.5 (384 dims)
            self._ensure_collection()
            self.is_active = True
        except Exception as e:
            logger.warning(f"EmbeddingService failed to initialize (Qdrant offline?): {e}")
            self.is_active = False

    def _ensure_collection(self) -> None:
        try:
            if not self.client.collection_exists(self.collection):
                # BGE-small outputs 384 dimensions
                self.client.create_collection(
                    collection_name=self.collection,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
                )
        except Exception as e:
            logger.warning(f"Could not check/create Qdrant collection: {e}")

    def embed_text(self, text: str) -> list[float]:
        if not hasattr(self, "model") or self.model is None:
            try:
                self.model = TextEmbedding()
            except Exception as e:
                logger.error(f"Failed to initialize TextEmbedding fallback: {e}")
                return [0.0] * 384
        try:
            # fastembed embed returns a generator
            embeddings = list(self.model.embed([text]))
            if len(embeddings) > 0:
                return embeddings[0].tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
        return [0.0] * 384

    def index_note(self, note_id: str, title: str, content: str) -> bool:
        if not self.is_active:
            return False
        try:
            text_to_embed = f"{title}\n{content}"
            vector = self.embed_text(text_to_embed)
            self.client.upsert(
                collection_name=self.collection,
                points=[
                    PointStruct(
                        id=note_id,
                        vector=vector,
                        payload={
                            "title": title,
                            "content": content,
                        },
                    )
                ],
            )
            return True
        except Exception as e:
            logger.error(f"Failed to index note {note_id} in Qdrant: {e}")
            return False

    def delete_note(self, note_id: str) -> bool:
        if not self.is_active:
            return False
        try:
            self.client.delete(
                collection_name=self.collection,
                points_selector=PointIdsList(points=[note_id]),
            )
            return True
        except Exception as e:
            logger.error(f"Failed to delete note {note_id} from Qdrant: {e}")
            return False

    def search_notes(self, query: str, limit: int = 5) -> list[dict]:
        if not self.is_active or not query.strip():
            return []
        try:
            query_vector = self.embed_text(query)
            res = self.client.query_points(
                collection_name=self.collection,
                query=query_vector,
                limit=limit,
            )
            results = []
            for hit in res.points:
                results.append(
                    {
                        "id": str(hit.id),
                        "score": float(hit.score),
                        "payload": hit.payload,
                    }
                )
            return results
        except Exception as e:
            logger.error(f"Error performing search in Qdrant: {e}")
            return []
