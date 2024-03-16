import pytest
from mongomock import MongoClient
from app.db.db_user import create_user
from app.schemas import UserCreate, LoginSchema, UserGet
from fastapi import HTTPException, status
from unittest.mock import patch
from app.auth import get_current_user
from pymongo.collection import Collection
from bson import ObjectId
from app.db.db_user import authenticate_user


@pytest.fixture
def mock_db():
    client = MongoClient()
    db = client["test_database"]
    yield db
    client.close()


@pytest.fixture
def user_data():
    return UserCreate(
        firstname="John",
        lastname="Doe",
        username="johndoe",
        email="john.doe@example.com",
        mobile="1234567890",
        country="USA",
        password="password123",
    )


@pytest.mark.asyncio
async def test_create_user_success(mock_db, user_data):
    created_user = await create_user(mock_db, user_data)

    assert created_user is not None
    assert created_user["email"] == user_data.email
    assert "id" in created_user


@pytest.mark.asyncio
async def test_create_user_email_exists(mock_db, user_data):
    mock_db.get_collection("users").insert_one({"email": user_data.email})

    with pytest.raises(HTTPException) as exc_info:
        await create_user(mock_db, user_data)

    assert exc_info.value.status_code == 400
    assert "Email already registered" in str(exc_info.value.detail)


@patch("app.db.hash.Hash.verify", return_value=False)
@pytest.mark.asyncio
async def test_authenticate_user_incorrect_email(mock_verify, mock_db):
    collection = mock_db.get_collection("users")
    collection.insert_one(
        {
            "_id": ObjectId(),
            "email": "correct@example.com",
            "password": "hashed_password",
        }
    )

    user_identifier = UserGet(email="incorrect@example.com")
    with pytest.raises(HTTPException) as exc_info:
        await authenticate_user(
            db=mock_db, identifier=user_identifier, password="any_password"
        )

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "User is not authorized"


@patch("app.db.hash.Hash.verify", return_value=False)
@pytest.mark.asyncio
async def test_authenticate_user_incorrect_password(mock_verify, mock_db):
    collection = mock_db.get_collection("users")
    collection.insert_one(
        {
            "_id": ObjectId(),
            "email": "user@example.com",
            "username": "testuser",
            "password": "hashed_correct_password",
        }
    )

    user_identifier = UserGet(email="user@example.com")
    with pytest.raises(HTTPException) as exc_info:
        await authenticate_user(
            db=mock_db, identifier=user_identifier, password="incorrect_password"
        )

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "User is not authorized"
