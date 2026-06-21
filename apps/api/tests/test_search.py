# ruff: noqa: E402, F401
import time

import pytest
from app.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Force test collection name for Qdrant isolation
settings.qdrant_collection = "test_knowledge_items"
# Force file-based SQLite path for multithreading compatibility
TEST_DB_FILE = "./test_api.db"
settings.database_url = f"sqlite:///{TEST_DB_FILE}"

from app.core.database import Base, get_db
from app.main import app
from app.models import Note

# Clear startup events to prevent background sync thread during tests
app.router.on_startup.clear()

from app.services.embedding_service import EmbeddingService
from fastapi.testclient import TestClient

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module", autouse=True)
def init_qdrant():
    es = EmbeddingService()
    if es.is_active:
        try:
            es.client.delete_collection(settings.qdrant_collection)
        except Exception:
            pass
        es._ensure_collection()
    yield
    if es.is_active:
        try:
            es.client.delete_collection(settings.qdrant_collection)
        except Exception:
            pass


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_indexing_on_crud_ops():
    es = EmbeddingService()
    if not es.is_active:
        pytest.skip("Qdrant is not running locally.")

    # 1. Create note
    create_resp = client.post(
        "/api/notes",
        json={"title": "FastAPI Authentication", "content": "How to set up JWT security."},
    )
    assert create_resp.status_code == 201
    note_id = create_resp.json()["id"]

    # Sleep to allow Qdrant index replication
    time.sleep(0.5)

    # Verify indexed in Qdrant
    hits = es.search_notes("FastAPI security")
    assert len(hits) > 0
    assert hits[0]["id"] == note_id
    assert hits[0]["payload"]["title"] == "FastAPI Authentication"

    # 2. Update note
    update_resp = client.put(
        f"/api/notes/{note_id}",
        json={
            "title": "FastAPI Caching",
            "content": "How to configure Redis caching mechanism.",
        },
    )
    assert update_resp.status_code == 200

    # Sleep to allow Qdrant index replication
    time.sleep(0.5)

    # Verify updated in Qdrant
    hits = es.search_notes("Redis caching")
    assert len(hits) > 0
    assert hits[0]["id"] == note_id
    assert hits[0]["payload"]["title"] == "FastAPI Caching"

    # 3. Delete note
    delete_resp = client.delete(f"/api/notes/{note_id}")
    assert delete_resp.status_code == 204

    # Sleep to allow Qdrant index replication
    time.sleep(0.5)

    # Verify deleted from Qdrant
    hits = es.search_notes("Redis caching")
    assert len(hits) == 0 or all(h["id"] != note_id for h in hits)


def test_search_endpoint():
    es = EmbeddingService()
    if not es.is_active:
        pytest.skip("Qdrant is not running locally.")

    # Insert test notes
    n1 = client.post(
        "/api/notes",
        json={
            "title": "Docker Setup",
            "content": "Docker compose files and volume mounts.",
        },
    ).json()
    n2 = client.post(
        "/api/notes",
        json={
            "title": "Vue State Management",
            "content": "Using Pinia store in Vue 3.",
        },
    ).json()

    # Sleep to allow Qdrant index replication
    time.sleep(0.5)

    # Search for containerization
    search_resp = client.post("/api/search", json={"query": "containers volumes docker"})
    assert search_resp.status_code == 200
    results = search_resp.json()
    assert len(results) > 0
    assert results[0]["id"] == n1["id"]
    assert "Docker" in results[0]["title"]

    # Search for frontend store
    search_resp = client.post("/api/search", json={"query": "pinia state vue"})
    assert search_resp.status_code == 200
    results = search_resp.json()
    assert len(results) > 0
    assert results[0]["id"] == n2["id"]
    assert "Vue" in results[0]["title"]
