from typing import List
from typing import Annotated, Any, Dict
from datetime import datetime
import pydantic
from pydantic import HttpUrl, BaseModel
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pymongo.database import Database
from app.schemas import (
    UserDisplay,
    UserCreate,
    LoginDisplay,
    UserGet,
    LoginSchema,
    User,
    SearchFlight,
    AirportSearchData2,
    AirportSearchData1,
    FavoriteFlight,
    SearchWeather,
    SearchOneWayFlight,
)
from app.db.database import get_db
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.jwttoken import verify_token
from app import config
from functools import lru_cache

# from app.db.db_user import create_user, get_all_users, get_user, update_user, delete_user
from app.db import db_user
import os
import requests
import logging
import httpx


router = APIRouter(
    prefix="/user",
    tags=["user"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Database = Depends(get_db)
):

    id_email = verify_token(
        token,
        HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="not authorized. Invalid Token",
        ),
    )

    user: User = await db_user.get_user(db, UserGet(id=id_email["id"]))
    return user


@router.post(
    "/register", response_model=UserDisplay, status_code=status.HTTP_201_CREATED
)
async def register_user(request: UserCreate, db: Database = Depends(get_db)):
    return await db_user.create_user(db, request)


@router.post("/login", response_model=LoginDisplay)
async def login(
    request: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Database = Depends(get_db),
):
    input = request.username

    if "@" in input:
        # input is an email
        userGet = UserGet(email=input)
    else:
        # input is a username
        userGet = UserGet(username=input)

    response = await db_user.authenticate_user(db, userGet, request.password)
    return response


@router.get("/me", response_model=UserDisplay, status_code=status.HTTP_200_OK)
async def read_users_me(
    current_user: Annotated[UserDisplay, Depends(get_current_user)]
):
    return current_user


# read one user
@router.get("/{id}", response_model=UserDisplay)
async def get_user(id: str, current_user: Annotated[User, Depends(get_current_user)]):
    if id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource.",
        )
    return current_user


# Airport Codes API


@router.post("/search-from-airport/")
async def search_from_airport(airport_data: AirportSearchData1):
    url = "https://tripadvisor16.p.rapidapi.com/api/v1/flights/searchAirport"
    querystring = {"query": airport_data.from_}
    headers = {
        "X-RapidAPI-Key": os.getenv("X_RAPIDAPI_KEY") or "",
        "X-RapidAPI-Host": os.getenv("X_RAPIDAPI_HOST") or "",
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers=headers,
            params=querystring,
            timeout=httpx.Timeout(timeout=40.0),
        )
    response_data = response.json()
    print(response_data)
    try:
        from_parent_id = response_data["data"][0]["details"]["parent_ids"][0]
        from_airport_code = response_data["data"][0]["airportCode"]

        print("From Parent ID:", from_parent_id)
        print("From Airport Code:", from_airport_code)

        return {"From_parent_id": from_parent_id, "FromAirportCode": from_airport_code}

    except (IndexError, KeyError) as e:
        print(e)
        raise HTTPException(
            status_code=400,
            detail=f"Error extracting from airport information: {str(e)}",
        )


@router.post("/search-to-airport/")
async def search_to_airport(search_data: AirportSearchData2):
    url = "https://tripadvisor16.p.rapidapi.com/api/v1/flights/searchAirport"
    querystring = {"query": search_data.to_}
    headers = {
        "X-RapidAPI-Key": os.getenv("X_RAPIDAPI_KEY", ""),
        "X-RapidAPI-Host": os.getenv("X_RAPIDAPI_HOST", ""),
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers=headers,
            params=querystring,
            timeout=httpx.Timeout(timeout=40.0),
        )
    response_data = response.json()

    try:
        to_parent_id = response_data["data"][0]["details"]["parent_ids"][0]
        to_airport_code = response_data["data"][0]["airportCode"]

        print("To Parent ID:", to_parent_id)
        print("To Airport Code:", to_airport_code)

        return {"To_parent_id": to_parent_id, "ToAirportCode": to_airport_code}

    except (IndexError, KeyError) as e:
        raise HTTPException(
            status_code=400, detail=f"Error extracting to airport information: {str(e)}"
        )


@router.post("/search-round-trip-flights/")
async def search_round_trip_flight(data: SearchFlight):
    url = "https://tripadvisor16.p.rapidapi.com/api/v1/flights/searchFlights"
    querystring = data.dict()
    headers = {
        "X-RapidAPI-Key": os.getenv("X_RAPIDAPI_KEY", ""),
        "X-RapidAPI-Host": os.getenv("X_RAPIDAPI_HOST", ""),
    }
    print(querystring)

    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, detail="Error fetching flight data"
            )

        flight_data = response.json()
        flight_pairs = []
        pair_info: Dict[str, Any] = {}

        for flight in flight_data["data"]["flights"]:
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


@router.post("/get-weather/")
async def get_weather(data: SearchWeather):
    api_key = os.getenv("WEATHER_API_KEY") or ""
    query = data.dict()
    print("Query is", query)
    city = query["city"]
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    response = requests.get(url)
    weather_info = []
    if response.status_code == 200:
        data = response.json()
        temp = data["main"]["temp"]
        desc = data["weather"][0]["main"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]

        weather_info.append(
            {
                "Temperature": temp,
                "Description": desc,
                "Feels": feels_like,
                "Humidity": humidity,
            }
        )
        return weather_info
    else:
        print("Error fetching weather data")


@router.post("/add_favorite_flight", response_model=list[FavoriteFlight])
async def add_favorite_flight(
    favorite_flights: list[FavoriteFlight],
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_db),
):
    results = []
    for favorite_flight in favorite_flights:
        flight_result = await db_user.add_favorite_flight(
            db, favorite_flight, current_user.id
        )
        if flight_result:
            results.append(favorite_flight)
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Could not save a favorite flight: {favorite_flight}",
            )
    if not results:
        raise HTTPException(
            status_code=500, detail="Could not save any favorite flights"
        )
    return results


@router.post("/add_save_trip/")
async def save_for_later(request: Request, db: Database = Depends(get_db)):
    try:
        request_json = await request.json()
        user_email = request_json.get("userEmail")
        users_collection = db["users"]
        user = users_collection.find_one({"email": user_email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user_id_str = str(user["_id"])
        request_json["user_id"] = user_id_str
        saved_trips_collection = db["saved_trips"]
        insert_result = saved_trips_collection.insert_one(request_json)

        return {
            "message": "Trip saved successfully",
            "id": str(insert_result.inserted_id),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.post("/search-one-way-flights/")
async def search_one_way_flight(data: SearchOneWayFlight):
    url = "https://tripadvisor16.p.rapidapi.com/api/v1/flights/searchFlights"
    querystring = data.dict()
    headers = {
        "X-RapidAPI-Key": os.getenv("X_RAPIDAPI_KEY", ""),
        "X-RapidAPI-Host": os.getenv("X_RAPIDAPI_HOST", ""),
    }
    print(querystring)

    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, detail="Error fetching flight data"
            )

        data = response.json()
        flights_info = []

        if "data" in data and "flights" in data["data"]:
            for flight in data["data"]["flights"]:
                for segment in flight["segments"]:
                    for leg in segment["legs"]:
                        airline_name = leg["operatingCarrier"]["displayName"]
                        flight_number = leg["flightNumber"]
                        departure_time_str = leg["departureDateTime"]
                        departure_with_tz = datetime.strptime(
                            departure_time_str, "%Y-%m-%dT%H:%M:%S%z"
                        )
                        final_departure_time = departure_with_tz.strftime("%H:%M")

                        arrival_time_str = leg["arrivalDateTime"]
                        arrival_with_tz = datetime.strptime(
                            arrival_time_str, "%Y-%m-%dT%H:%M:%S%z"
                        )
                        final_arrival_time = arrival_with_tz.strftime("%H:%M")

                        time_taken = arrival_with_tz - departure_with_tz
                        hours, remainder = divmod(time_taken.seconds, 3600)
                        minutes, _ = divmod(remainder, 60)

                        number_of_stops = (
                            "Direct"
                            if leg["numStops"] == 0
                            else f"{leg['numStops']} Stop(s)"
                        )

                        airline_logo = leg["operatingCarrier"]["logoUrl"]

                        flights_info.append(
                            {
                                "Airline Name": airline_name,
                                "Flight Number": flight_number,
                                "Departure Time": final_departure_time,
                                "Arrival Time": final_arrival_time,
                                "Duration": f"{hours:02d} h {minutes:02d} m",
                                "Number of Stops": number_of_stops,
                                "Price of Flight": flight["purchaseLinks"][0][
                                    "totalPrice"
                                ],
                                "Airline Logo": airline_logo,
                            }
                        )

        return flights_info

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
