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

router = APIRouter(
    prefix="/attraction",
    tags=["attractions"],
)


@router.post("/search-attractions", response_model=list[AttractionData])
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
            print(response.request.url)

            print(response)
            print(response.history)

            print(response.text)
            raise HTTPException(
                status_code=500,
                detail=response.json().get("results", "Api request failed"),
            )

        data = response.json()
        attractions_data = data.get("results", {}).get("data", [])
        filtered_data = []
        for attraction in attractions_data:
            photo_data = attraction.get("photo", {}).get("images", {})
            photos = PhotoUrls(
                small=photo_data.get("small", {}).get("url", ""),
                medium=photo_data.get("medium", {}).get("url", ""),
                large=photo_data.get("large", {}).get("url", ""),
                original=photo_data.get("original", {}).get("url", ""),
            )
            subcategory = [
                sub.get("name", "") for sub in attraction.get("subcategory", [])
            ]
            subtype = [subs.get("name", "") for subs in attraction.get("subtype", [])]
            booking_data = attraction.get("booking", {})
            booking = Booking(
                provider_name=booking_data.get("provider", ""),
                url=booking_data.get("url", ""),
            )
            animal_data = attraction.get("animal_welfare_tag", {})
            animal_feature = AnimalTag(
                tag=animal_data.get("tag_text", ""),
                msg_header=animal_data.get("msg_header", ""),
                msg_body=animal_data.get("msg_body", ""),
                learn_more_text=animal_data.get("leanr_more_text", ""),
                education_portal_url=animal_data.get("education_portal_url", ""),
            )

            offer_list = []
            for offer in attraction.get("offer_group", {}).get("offer_list", []):
                offer_list.append(TourOfferDetail(**offer))

            filtered_data.append(
                {
                    "location_id": attraction.get("location_id"),
                    "attraction_name": attraction.get("name"),
                    "attraction_reviews_count": attraction.get("num_reviews"),
                    "attraction_location": attraction.get("location_string"),
                    "attraction_photos": photos,
                    "attraction_raw_ranking": attraction.get("raw_ranking"),
                    "attraction_rating": attraction.get("ranking"),
                    "attraction_description": attraction.get("description"),
                    "attraction_weburl": attraction.get("web_url"),
                    "attraction_category": subcategory,
                    "attraction_phone": attraction.get("phone"),
                    "attraction_website": attraction.get("website"),
                    "attraction_address": attraction.get("address"),
                    "attraction_subtype": subtype,
                    "attraction_offer_tours": offer_list,
                    "attraction_booking": booking,
                    "attraction_animal_tag": animal_feature,
                }
            )
            print(filtered_data)
            return filtered_data
