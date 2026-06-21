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


def test_create_and_get_note():
    response = client.post(
        "/api/notes",
        json={
            "title": "Test Title",
            "content": "Test Content",
            "summary": "Test Summary",
            "category": "Test Category",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Title"
    assert data["content"] == "Test Content"
    assert data["summary"] == "Test Summary"
    assert data["category"] == "Test Category"
    assert "id" in data

    note_id = data["id"]

    response = client.get(f"/api/notes/{note_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Title"
    assert data["content"] == "Test Content"
    assert data["summary"] == "Test Summary"
    assert data["category"] == "Test Category"


def test_list_notes():
    client.post("/api/notes", json={"title": "Note 1", "content": "Content 1"})
    client.post("/api/notes", json={"title": "Note 2", "content": "Content 2"})

    response = client.get("/api/notes")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Note 2"
    assert data[1]["title"] == "Note 1"


def test_update_note():
    create_response = client.post(
        "/api/notes", json={"title": "Original Title", "content": "Original Content"}
    )
    note_id = create_response.json()["id"]

    update_response = client.put(f"/api/notes/{note_id}", json={"title": "Updated Title"})
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["title"] == "Updated Title"
    assert data["content"] == "Original Content"

    update_response = client.put(
        f"/api/notes/{note_id}",
        json={
            "title": "New Title",
            "content": "New Content",
            "summary": "New Summary",
            "category": "New Category",
        },
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["title"] == "New Title"
    assert data["content"] == "New Content"
    assert data["summary"] == "New Summary"
    assert data["category"] == "New Category"


def test_delete_note():
    create_response = client.post("/api/notes", json={"title": "To Delete", "content": "To Delete"})
    note_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/notes/{note_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/notes/{note_id}")
    assert get_response.status_code == 404
