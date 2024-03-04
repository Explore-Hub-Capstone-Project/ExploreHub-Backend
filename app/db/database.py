from pymongo import MongoClient
from typing import Dict, Any
from app.config import settings
import os


def get_db():
    mongodb_uri = settings.MONGODB_URI

    # if the env var MONGODB_URI exists
    # then use it as the uri for MongoClient
    # otherwise use the one in settings.connection_string
    client: MongoClient[Dict[str, Any]] = MongoClient(mongodb_uri, settings.mongo_port)
    db = client[settings.database_name]

    try:
        yield db

    finally:
        client.close()
