# In oauth.py, adjust get_current_user to fetch user details
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pymongo import MongoClient
from jose import jwt, JWTError
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


mongodb_uri = os.getenv("MONGODB_URI")
port = 8000
client = MongoClient(mongodb_uri, port)
db = client["User"]
users_collection = db["users"]


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
        user = users_collection.find_one({"email": email})
        if user is None:
            raise credentials_exception
        return user  # Return the user document from the database
    except JWTError:
        raise credentials_exception
