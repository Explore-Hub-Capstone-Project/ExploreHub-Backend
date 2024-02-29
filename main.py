import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
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
from datetime import datetime
from fastapi.security import OAuth2PasswordBearer
import requests

import httpx
from models import (
    AirportSearchData1,
    AirportSearchData2,
    User,
    Token,
    TokenData,
    UserCreate,
    LoginSchema,
    SearchFlight,
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


@app.post("/search-round-trip-flights/")
async def search_round_trip_flight(data: SearchFlight):
    url = "https://tripadvisor16.p.rapidapi.com/api/v1/flights/searchFlights"
    querystring = data.dict()
    headers = {
        "X-RapidAPI-Key": os.getenv("X_RAPIDAPI_KEY"),
        "X-RapidAPI-Host": os.getenv("X_RAPIDAPI_HOST"),
    }
    print(querystring)

    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, detail="Error fetching flight data"
            )

        data = response.json()
        flight_pairs = []
        pair_info: Dict[str, Any] = {}

        for flight in data["data"]["flights"]:
            pair_info = {"outbound": None, "return": None, "price": None}

            if flight["segments"]:
                outbound_leg = flight["segments"][0]["legs"][0]
                return_leg = (
                    flight["segments"][1]["legs"][0]
                    if len(flight["segments"]) > 1
                    else None
                )

                departure_time_outbound = datetime.fromisoformat(
                    outbound_leg["departureDateTime"]
                )
                arrival_time_outbound = datetime.fromisoformat(
                    outbound_leg["arrivalDateTime"]
                )
                duration_outbound = arrival_time_outbound - departure_time_outbound
                hours, remainder = divmod(duration_outbound.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)

                pair_info["outbound"] = {
                    "Airline Name": outbound_leg["operatingCarrier"]["displayName"],
                    "Flight Number": outbound_leg["flightNumber"],
                    "Departure Time": departure_time_outbound.strftime("%H:%M"),
                    "Arrival Time": arrival_time_outbound.strftime("%H:%M"),
                    "Duration": f"{hours:02d} h {minutes:02d} m",
                    "Number of Stops": outbound_leg["numStops"],
                    "Airline Logo": outbound_leg["operatingCarrier"]["logoUrl"],
                    "Source City Code": outbound_leg["originStationCode"],
                    "Destination City Code": outbound_leg["destinationStationCode"],
                }

                if return_leg:

                    departure_time_return = datetime.fromisoformat(
                        return_leg["departureDateTime"]
                    )
                    arrival_time_return = datetime.fromisoformat(
                        return_leg["arrivalDateTime"]
                    )
                    duration_return = arrival_time_return - departure_time_return
                    hours, remainder = divmod(duration_return.seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)

                    pair_info["return"] = {
                        "Airline Name": return_leg["operatingCarrier"]["displayName"],
                        "Flight Number": return_leg["flightNumber"],
                        "Departure Time": departure_time_return.strftime("%H:%M"),
                        "Arrival Time": arrival_time_return.strftime("%H:%M"),
                        "Duration": f"{hours:02d} h {minutes:02d} m",
                        "Number of Stops": return_leg["numStops"],
                        "Airline Logo": return_leg["operatingCarrier"]["logoUrl"],
                        "Source City Code": return_leg["originStationCode"],
                        "Destination City Code": return_leg["destinationStationCode"],
                    }

                if flight["purchaseLinks"]:
                    pair_info["price"] = flight["purchaseLinks"][0]["totalPrice"]

                flight_pairs.append(pair_info)

        return flight_pairs

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
