from pprint import pprint
from fastapi import APIRouter, HTTPException
from app.schemas import (
    LocationSearchResponse,
    Location,
    HotelsFilterResponse,
    HotelFilter,
    LocInfo,
    HotelDetails,
    HotelDetailDisplay,
    HotelData,
    PhotoItem,
    PhotoItemSizeDynamic,
    Photo,
    Price,
    Review,
    Locations,
    Restaurant,
    Attraction,
    QuestionAnswer,
    MemberProfile,
    ProfileImage,
    TopAnswer,
    AmenityDetail,
)
import os
import httpx

# from typing import List

router = APIRouter(
    prefix="/hotel",
    tags=["hotels"],
)


@router.post("/search-location", response_model=LocationSearchResponse)
async def search_location(location_data: Location):
    url = "https://tripadvisor16.p.rapidapi.com/api/v1/hotels/searchLocation"
    headers = {
        "X-RapidAPI-Key": os.getenv("X_RAPIDAPI_KEY"),
        "X-RapidAPI-Host": "tripadvisor16.p.rapidapi.com",
    }
    params = {"query": location_data.location}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, detail="API call failed"
            )

        data = response.json()
        locs_data = data.get("data", [])

        print(locs_data)
        # Extract relevant hotel information and construct the response
        locs = [
            LocInfo(
                title=loc["title"],
                documentId=loc["documentId"],
                secondaryText=loc["secondaryText"],
            )
            for loc in locs_data
            # if hotel.get("trackingItems") == "hotel"
        ]

        return LocationSearchResponse(locs=locs)


@router.post("/get-hotels-filter", response_model=HotelsFilterResponse)
async def hotels_filter(filter: HotelFilter):
    # url = "https://tripadvisor16.p.rapidapi.com/api/v1/hotels/searchLocation"
    url = "https://tripadvisor16.p.rapidapi.com/api/v1/hotels/getHotelsFilter"
    headers = {
        "X-RapidAPI-Key": os.getenv("X_RAPIDAPI_KEY"),
        "X-RapidAPI-Host": "tripadvisor16.p.rapidapi.com",
    }
    params = {
        "geoId": filter.geoId,
        "checkIn": filter.checkIn,
        "checkOut": filter.checkOut,
    }
    print(f"Requesting {url} with params {params} and headers {headers}")
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url, headers=headers, params=params, timeout=httpx.Timeout(timeout=15.0)
        )
        print("Response received:", response)  # Log the response data
        if response.status_code == 200:
            response = response.json()
            print("data received", response)
            if response.get("status") and "data" in response:
                return HotelsFilterResponse(**response["data"])

            elif "message" in response:
                error_detail = "API Error: " + str(response.get("message"))
                raise HTTPException(status_code=400, detail=error_detail)
            else:
                raise HTTPException(
                    status_code=400, detail="Unexpected API response structure"
                )
        else:
            print("Failed to fetch data:", response.text)
            raise HTTPException(
                status_code=response.status_code, detail="API call failed"
            )


@router.post("/search-hotels", response_model=list[HotelData])
async def search_hotels(filter: HotelFilter):
    url = "https://tripadvisor16.p.rapidapi.com/api/v1/hotels/searchHotels"
    headers = {
        "X-RapidAPI-Key": os.getenv("X_RAPIDAPI_KEY"),
        "X-RapidAPI-Host": "tripadvisor16.p.rapidapi.com",
    }
    params = {
        "geoId": filter.geoId,
        "checkIn": filter.checkIn,
        "checkOut": filter.checkOut,
        "pageNumber": "1",
        "currencyCode": "USD",
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url, headers=headers, params=params, timeout=httpx.Timeout(timeout=20.0)
        )
        print(response)
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, detail="API call failed"
            )
        data = response.json()
        # print(data)
        hotels_data = data.get("data", {}).get("data", [])
        filtered_hotel_data = []
        for hotel in hotels_data:
            bubble_rating = {
                "rating": float(hotel.get("bubbleRating", {}).get("rating", 0)),
                "count": hotel.get("bubbleRating", {}).get("count", "0"),
            }

            photo_items = [
                PhotoItem(
                    sizes=PhotoItemSizeDynamic(
                        maxHeight=photo["sizes"]["maxHeight"],
                        maxWidth=photo["sizes"]["maxWidth"],
                        urlTemplate=photo["sizes"]["urlTemplate"],
                    )
                )
                for photo in hotel.get("cardPhotos", [])
            ]
            filtered_hotel_data.append(
                {
                    "accomodation_id": hotel.get("id"),
                    "accomodation": hotel.get("title"),
                    "breakfast_info": hotel.get("primaryInfo"),
                    "accomodation_region": hotel.get("secondaryInfo"),
                    "accomodation_rating": bubble_rating,
                    "accomodation_provider": hotel.get("provider"),
                    "priceForDisplay": hotel.get("priceForDisplay"),
                    "strikethroughPrice": hotel.get("strikethroughPrice"),
                    "priceDetails": hotel.get("priceDetails"),
                    "priceSummary": hotel.get("priceSummary"),
                    "accomodation_photos": photo_items,
                }
            )
        print(filtered_hotel_data)
        return filtered_hotel_data

    # return [HotelData(**hotel) for hotel in filtered_hotel_data]


@router.post("/get-hotels-details", response_model=HotelDetailDisplay)
async def hotel_details(details: HotelDetails):
    url = "https://tripadvisor16.p.rapidapi.com/api/v1/hotels/getHotelDetails"
    headers = {
        "X-RapidAPI-Key": os.getenv("X_RAPIDAPI_KEY"),
        "X-RapidAPI-Host": "tripadvisor16.p.rapidapi.com",
    }
    params = {
        "id": details.accomodation_id,
        "checkIn": details.checkIn,
        "checkOut": details.checkOut,
        "currency": "USD",
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url, headers=headers, params=params, timeout=httpx.Timeout(timeout=20.0)
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, detail="API call failed"
            )
        print(response.json())
        data = response.json().get("data")
        photo_data = data.get("photos", [])
        photos = [
            Photo(
                maxHeight=photo["maxHeight"],
                maxWidth=photo["maxWidth"],
                urlTemplate=photo["urlTemplate"],
            )
            for photo in photo_data
        ]
        price_data = data.get("price", {})
        price = Price(
            displayPrice=price_data.get("displayPrice"),
            strikeThroughPrice=price_data.get("strikeThroughPrice"),
            status=price_data.get("status"),
            providerName=price_data.get("providerName"),
            freeCancellation=price_data.get("freeCancellation"),
            pricingPeriod=price_data.get("pricingPeriod"),
        )
        review_data = data.get("reviews", {})
        review = Review(
            title=review_data.get("title"),
            text=review_data.get("text"),
            bubbleRatingText=review_data.get("bubbleRatingText"),
            publishedDate=review_data.get("publishedDate"),
            userProfile=review_data.get("userProfile"),
            photos=review_data.get("photos"),
        )
        location_data = data.get("location", {})
        loc = Locations(
            title=location_data.get("title"),
            address=location_data.get("address"),
            neighborhood=location_data.get("neighborhood", {}),
            gettingThere=location_data.get("gettingThere", {}),
            walkability=location_data.get("walkability"),
        )
        restaurant_data = data.get("restaurantsNearby", {}).get("content", [])
        restaurants_nearby = [
            Restaurant(
                restaurant_name=restaurant.get("title"),
                bubbleRating=restaurant.get("bubbleRating", {}),
                restauranttype=restaurant.get("primaryInfo"),
                distance=restaurant.get("distance"),
                restaurantPhoto=Photo(
                    maxHeight=restaurant.get("cardPhoto", {}).get("maxHeight"),
                    maxWidth=restaurant.get("cardPhoto", {}).get("maxWidth"),
                    urlTemplate=restaurant.get("cardPhoto", {}).get("urlTemplate"),
                ),
            )
            for restaurant in restaurant_data
        ]

        attractions_nearby_data = data.get("attractionsNearby", {}).get("content", [])
        attractions_nearby = [
            Attraction(
                attraction_name=attraction.get("title"),
                bubbleRating=attraction.get("bubbleRating", {}),
                primaryInfo=attraction.get("primaryInfo"),
                distance=attraction.get("distance"),
                attractionPhoto=(
                    Photo(
                        maxHeight=attraction.get("cardPhoto", {}).get("maxHeight", 0),
                        maxWidth=attraction.get("cardPhoto", {}).get("maxWidth", 0),
                        urlTemplate=attraction.get("cardPhoto", {}).get("urlTemplate"),
                    )
                    if attraction.get("cardPhoto")
                    else None
                ),
            )
            for attraction in attractions_nearby_data
        ]
        qa_data = data.get("qA", {}).get("content", [])
        qas = [
            QuestionAnswer(
                title=qa.get("title"),
                writtenDate=qa.get("writtenDate"),
                memberProfile=(
                    MemberProfile(
                        profileImage=ProfileImage(
                            maxHeight=qa.get("memberProfile", {})
                            .get("profileImage", {})
                            .get("maxHeight"),
                            maxWidth=qa.get("memberProfile", {})
                            .get("profileImage", {})
                            .get("maxWidth"),
                            urlTemplate=qa.get("memberProfile", {})
                            .get("profileImage", {})
                            .get("urlTemplate"),
                        )
                    )
                    if qa.get("memberProfile")
                    else None
                ),
                topAnswer=(
                    TopAnswer(
                        memberProfile=MemberProfile(
                            profileImage=ProfileImage(
                                maxHeight=qa.get("topAnswer", {})
                                .get("memberProfile", {})
                                .get("profileImage", {})
                                .get("maxHeight"),
                                maxWidth=qa.get("topAnswer", {})
                                .get("memberProfile", {})
                                .get("profileImage", {})
                                .get("maxWidth"),
                                urlTemplate=qa.get("topAnswer", {})
                                .get("memberProfile", {})
                                .get("profileImage", {})
                                .get("urlTemplate"),
                            )
                        )
                    )
                    if qa.get("topAnswer")
                    else None
                ),
            )
            for qa in qa_data
        ]
        amenities_data = data.get("amenitiesScreen", [])
        amenities = [
            AmenityDetail(
                title=amenity.get("title"), content=amenity.get("content", [])
            )
            for amenity in amenities_data
        ]

        selected_data = {
            "photos": photos,
            "accomodation_name": data.get("title"),
            "rating": data.get("rating"),
            "numberReviews": data.get("numberReviews"),
            "rankingDetails": data.get("rankingDetails"),
            "price": price,
            "reviews": review,
            "Location": loc,
            "restaurantsNearby": restaurants_nearby,
            "attractionsNearby": attractions_nearby,
            "qA": qas,
            "amenitiesScreen": amenities,
        }
        pprint(selected_data)
        return selected_data
