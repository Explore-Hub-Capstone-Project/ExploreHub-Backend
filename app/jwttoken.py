from datetime import datetime, timedelta
from pprint import pprint
from typing import Any
from jose import JWTError, jwt

# from main import TokenData


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3000


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, credentials_exception: Exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        pprint(payload)
        email_payload: Any | None = payload.get("user_email", None)
        id_payload: Any | None = payload.get("user_id", None)
        if email_payload is None or not isinstance(email_payload, str):
            print({email_payload: email_payload}, credentials_exception)
            raise credentials_exception
        if id_payload is None or not isinstance(id_payload, str):
            print({id_payload: id_payload}, credentials_exception)
            raise credentials_exception
        return {"email": email_payload, "id": id_payload}
        # username: str = str(username_payl)
    except JWTError:
        print({"JWTError": str(JWTError)}, credentials_exception)
        raise credentials_exception
