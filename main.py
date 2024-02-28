import os
from dotenv import load_dotenv
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Request, status, APIRouter
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, EmailStr, Field
from hashing import Hash
from jwttoken import create_access_token
from oauth import get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from fastapi.security import OAuth2PasswordBearer
import httpx
from models import (
    AirportSearchData1,
    AirportSearchData2,
    User,
    Token,
    TokenData,
    UserCreate,
    LoginSchema,
)


app = FastAPI()
origins = [
    "http://localhost:3000",
    "http://localhost:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()
mongodb_uri = os.getenv("MONGODB_URI")
port = 8000
client = MongoClient(mongodb_uri, port)
db = client["User"]
users_collection = db["users"]


@app.get("/")
def read_root(current_user: User = Depends(get_current_user)):
    return {"data": "Hello OWrld"}


@app.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    user_dict = user.dict(exclude={"confirmPassword"})
    user_dict["password"] = Hash.bcrypt(user.password)
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    users_collection.insert_one(user_dict)
    return {"message": "User created successfully"}


@app.post("/login")
async def login(user_credentials: LoginSchema):
    user = db["users"].find_one({"email": user_credentials.email})
    if not user or not Hash.verify(user["password"], user_credentials.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid login credentials"
        )

    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/userinfo")
async def read_user_info(current_user: dict = Depends(get_current_user)):
    user_identifier = current_user.get("email")
    print("User identifier:", user_identifier)
    if not user_identifier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User identifier not found"
        )

    user_info = users_collection.find_one({"email": user_identifier})
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user_full_name = f"{user_info.get('firstname', '')} {user_info.get('lastname', '')}"
    return {"name": user_full_name.strip()}


# Airport Codes API


@app.post("/search-from-airport/")
async def search_from_airport(data: AirportSearchData1):
    url = "https://tripadvisor16.p.rapidapi.com/api/v1/flights/searchAirport"
    querystring = {"query": data.from_}
    headers = {
        "X-RapidAPI-Key": os.getenv("X_RAPIDAPI_KEY"),
        "X-RapidAPI-Host": os.getenv("X_RAPIDAPI_HOST"),
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=querystring)
    data = response.json()

    try:
        from_parent_id = data["data"][0]["details"]["parent_ids"][0]
        from_airport_code = data["data"][0]["airportCode"]

        print("From Parent ID:", from_parent_id)
        print("From Airport Code:", from_airport_code)

        return {"From_parent_id": from_parent_id, "FromAirportCode": from_airport_code}

    except (IndexError, KeyError) as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error extracting from airport information: {str(e)}",
        )


@app.post("/search-to-airport/")
async def search_to_airport(data: AirportSearchData2):
    url = "https://tripadvisor16.p.rapidapi.com/api/v1/flights/searchAirport"
    querystring = {"query": data.to_}
    headers = {
        "X-RapidAPI-Key": os.getenv("X_RAPIDAPI_KEY"),
        "X-RapidAPI-Host": os.getenv("X_RAPIDAPI_HOST"),
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=querystring)
    data = response.json()

    try:
        to_parent_id = data["data"][0]["details"]["parent_ids"][0]
        to_airport_code = data["data"][0]["airportCode"]

        print("To Parent ID:", to_parent_id)
        print("To Airport Code:", to_airport_code)

        return {"To_parent_id": to_parent_id, "ToAirportCode": to_airport_code}

    except (IndexError, KeyError) as e:
        raise HTTPException(
            status_code=400, detail=f"Error extracting to airport information: {str(e)}"
        )
