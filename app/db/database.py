from pymongo import MongoClient
from typing import Dict, Any
from app.config import settings
import os


def get_db():
    mongodb_uri = settings.MONGODB_URI
    client: MongoClient[Dict[str, Any]] = MongoClient(mongodb_uri, settings.port)
    db = client[settings.database_name]

    try:
        yield db

    finally:
        client.close()
