import pytest
import mongomock
from app.db.db_user import create_user
from app.schemas import UserCreate  # Adjust import as necessary
from fastapi.exceptions import HTTPException


@pytest.fixture
def mock_db():
    return mongomock.MongoClient().db


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
