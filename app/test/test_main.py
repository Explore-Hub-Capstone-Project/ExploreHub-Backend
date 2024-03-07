from fastapi.testclient import TestClient
from mongomock import MongoClient as MongoMockClient
from app.db.database import get_db
from app.config import settings
from pymongo import MongoClient
from typing import Dict, Any
from app.main import app
from unittest.mock import patch
from app.schemas import User

client = TestClient(app)


def get_mock_db():
    client = MongoMockClient()
    db = client["test_db"]
    try:
        yield db
    finally:
        client.close()


app.dependency_overrides[get_db] = get_mock_db


def test_mock_database_operations():
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword",
    }
    db = next(get_mock_db())
    users_collection = db["users"]
    users_collection.insert_one(user_data)
    retrieved_user = users_collection.find_one({"username": "testuser"})
    assert (
        retrieved_user is not None
    ), "User should have been found in the mock database"
    assert (
        retrieved_user["email"] == "testuser@example.com"
    ), "User email should match the inserted data"
    users_collection.delete_one({"username": "testuser"})
    deleted_user = users_collection.find_one({"username": "testuser"})
    assert deleted_user is None, "User should have been deleted from the mock database"


def test_create_user_success():
    user_data = {
        "firstname": "John",
        "lastname": "Doe",
        "username": "johndoe",
        "email": "john.doe@example.com",
        "mobile": "1234567890",
        "country": "Country",
        "password": "password",
    }
    response = client.post("/user/register", json=user_data)
    assert response.status_code == 201
    assert response.json()["email"] == user_data["email"]
