from fastapi import APIRouter, HTTPException
from app.schemas import (
    AttractionData,
    AttractionRequest,
    TourOfferDetail,
    PhotoUrls,
    Booking,
    AnimalTag,
)
import os
import httpx
from typing import List

router = APIRouter(prefix="/attraction", tags=["attractions"])


@router.post("/search-attractions", response_model=List[AttractionData])
async def search_attractions(detail: AttractionRequest):
    url = "https://tourist-attraction.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": os.getenv("X_RAPIDAPI_KEY"),
        "X-RapidAPI-Host": "tourist-attraction.p.rapidapi.com",
    }
    payload = {
        "location_id": detail.location_id,
        "language": detail.language,
        "currency": "USD",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url, headers=headers, data=payload, timeout=httpx.Timeout(timeout=15.0)
        )

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="API request failed")

        data = response.json()
        attractions_data = data.get("results", {}).get("data", [])
        filtered_data = []

        for attraction in attractions_data[:10]:  # Limit to 10 attractions
            photos = PhotoUrls(
                small=attraction.get("photo", {})
                .get("images", {})
                .get("small", {})
                .get("url"),
                medium=attraction.get("photo", {})
                .get("images", {})
                .get("medium", {})
                .get("url"),
                large=attraction.get("photo", {})
                .get("images", {})
                .get("large", {})
                .get("url"),
                original=attraction.get("photo", {})
                .get("images", {})
                .get("original", {})
                .get("url"),
            )
            offer_list = [
                TourOfferDetail(**offer)
                for offer in attraction.get("offer_group", {}).get("offer_list", [])
            ]
            booking_data = attraction.get("booking", {})
            booking = Booking(
                provider_name=booking_data.get("provider"),
                url=booking_data.get("url"),
            )
            animal_data = attraction.get("animal_welfare_tag", {})
            animal_feature = AnimalTag(
                tag=animal_data.get("tag_text"),
                msg_header=animal_data.get("msg_header"),
                msg_body=animal_data.get("msg_body"),
                learn_more_text=animal_data.get("learn_more_text"),
                education_portal_url=animal_data.get("education_portal_url"),
            )

            filtered_data.append(
                AttractionData(
                    location_id=attraction.get("location_id"),
                    attraction_name=attraction.get("name"),
                    attraction_reviews_count=int(attraction.get("num_reviews", 0)),
                    attraction_location=attraction.get("location_string"),
                    attraction_photos=photos,
                    attraction_raw_ranking=float(attraction.get("raw_ranking", 0)),
                    attraction_rating=attraction.get("ranking"),
                    attraction_description=attraction.get("description"),
                    attraction_weburl=attraction.get("web_url"),
                    attraction_category=[
                        sub.get("name", "") for sub in attraction.get("subcategory", [])
                    ],
                    attraction_phone=attraction.get("phone"),
                    attraction_website=attraction.get("website"),
                    attraction_address=attraction.get("address"),
                    attraction_subtype=[
                        subs.get("name", "") for subs in attraction.get("subtype", [])
                    ],
                    attraction_offer_tours=offer_list,
                    attraction_booking=booking,
                    attraction_animal_tag=animal_feature,
                )
            )

        return filtered_data
