import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import (
    get_db,
)
from mongomock import MongoClient


@pytest.fixture
def mock_db():
    client = MongoClient()
    db = client["test_database"]
    yield db
    client.close()


@pytest.fixture
def override_get_db(mock_db):
    async def _override_get_db():
        return mock_db

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client


@pytest.mark.asyncio
async def test_add_save_trip_success(test_client, override_get_db, mock_db):
    user_email = "user@example.com"
    mock_db["users"].insert_one({"email": user_email, "_id": "user_id_123"})
    trip_details = {"userEmail": user_email, "tripDetails": "Trip to Hawaii"}

    response = test_client.post("/user/add_save_trip/", json=trip_details)
    assert response.status_code == 200
    assert response.json()["message"] == "Trip saved successfully"

    saved_trip = mock_db["saved_trips"].find_one({"userEmail": user_email})
    assert saved_trip is not None
    assert saved_trip["tripDetails"] == "Trip to Hawaii"
