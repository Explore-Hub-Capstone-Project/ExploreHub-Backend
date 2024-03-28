from fastapi import APIRouter, HTTPException
from app.schemas import AttractionsMain
import os
import httpx
import requests

router = APIRouter(
    prefix="/attractions",
    tags=["attractions"],
)


@router.post("/get-attractions")
async def search_attraction(data: AttractionsMain):
    url = "https://tourist-attraction.p.rapidapi.com/search"

    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "X-RapidAPI-Key": os.getenv("X_RAPIDAPI_KEY"),
        "X-RapidAPI-Host": "tourist-attraction.p.rapidapi.com",
    }

    params = {
        "location_id": data.location_id,
        "language": data.language,
        "currency": data.currency,
    }

    async with httpx.AsyncClient() as request:
        response = await request.get(
            url, headers=headers, params=params, timeout=httpx.Timeout(timeout=15.0)
        )
        if response.status_code == 200:
            response = response.json()
            print("data received", response)
            if response.get("status") in response:
                return response

        else:
            print("Failed to fetch data:", response.text)
            raise HTTPException(
                status_code=response.status_code, detail="API call failed"
            )
