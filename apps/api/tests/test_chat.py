# ruff: noqa: E402, F401
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


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_chat_graceful_offline_fallback():
    # Test POST /api/chat when Ollama is offline (default)
    # First, let's create a note to retrieve as context
    client.post(
        "/api/notes",
        json={
            "title": "FastAPI CORS setup instructions",
            "content": "Add CORSMiddleware to allow cross-origin requests.",
        },
    )

    response = client.post(
        "/api/chat",
        json={"message": "FastAPI CORS configure"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    # Fallback message should list the FastAPI CORS note
    assert "offline" in data["answer"] or "⚠️" in data["answer"]
    assert len(data["sources"]) > 0
    assert data["sources"][0]["title"] == "FastAPI CORS setup instructions"


def test_chat_with_mocked_ollama(monkeypatch):
    # Mock LLMService.generate_response to simulate a successful Ollama response
    from app.services.llm_service import LLMService

    def mock_generate_response(self, prompt: str) -> str:
        return "To configure CORS in FastAPI, import CORSMiddleware and add it."

    monkeypatch.setattr(LLMService, "generate_response", mock_generate_response)

    client.post(
        "/api/notes",
        json={
            "title": "FastAPI CORS setup instructions",
            "content": "Add CORSMiddleware to allow cross-origin requests.",
        },
    )

    response = client.post(
        "/api/chat",
        json={"message": "How to set up CORS?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "CORSMiddleware" in data["answer"]
    assert len(data["sources"]) > 0
    assert data["sources"][0]["title"] == "FastAPI CORS setup instructions"
