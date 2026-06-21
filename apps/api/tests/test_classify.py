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


def test_classify_endpoint():
    # Test POST /api/classify
    response = client.post(
        "/api/classify",
        json={
            "title": "Configuring CORS in FastAPI",
            "content": "CORS middleware configuration instructions and setup guide.",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "category" in data
    assert "confidence" in data
    assert data["category"] == "FastAPI"
    assert data["confidence"] > 0.0


def test_auto_classification_on_create():
    # Create note without a category
    response = client.post(
        "/api/notes",
        json={
            "title": "Python list comprehension tutorial",
            "content": "A simple guide to list comprehensions and generators in Python.",
        },
    )
    assert response.status_code == 201
    data = response.json()
    # Should automatically classify as Python
    assert data["category"] == "Python"
    assert "categoryConfidence" in data
    assert data["categoryConfidence"] is not None
    assert data["categoryConfidence"] > 0.0


def test_auto_classification_on_update():
    # Create a categorized note
    create_response = client.post(
        "/api/notes",
        json={
            "title": "Initial draft",
            "content": "Work in progress notes.",
            "category": "Personal",
        },
    )
    note_id = create_response.json()["id"]
    assert create_response.json()["category"] == "Personal"

    # Update to clear the category and provide ML content
    update_response = client.put(
        f"/api/notes/{note_id}",
        json={
            "title": "Feature extraction in Neural Networks",
            "content": "CNN spatial feature extraction convolutional layer study.",
            "category": "",  # clear category to trigger auto-classification
        },
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["category"] == "Machine Learning"
    assert data["categoryConfidence"] is not None
    assert data["categoryConfidence"] > 0.0
