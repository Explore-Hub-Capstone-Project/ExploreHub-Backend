from pymongo import MongoClient
from typing import Dict, Any
from app.config import settings
import os


def get_db():
    mongodb_uri = settings.MONGODB_URI
    client: MongoClient[Dict[str, Any]] = MongoClient(mongodb_uri, settings.PORT)
    db = client[settings.DATABASE_NAME]

    try:
        yield db

    finally:
        client.close()
