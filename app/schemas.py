from pydantic import BaseModel, EmailStr, Field, HttpUrl, AnyHttpUrl
import re
from typing import List, Optional, Union


# showing to user these info
class UserDisplay(BaseModel):
    id: str
    firstname: str
    lastname: str
    username: str
    email: str
    mobile: str
    country: str
    model_config = {
        "from_attributes": True,
    }


# valdating user input to create info
class UserCreate(BaseModel):
    firstname: str = Field(..., min_length=1)
    lastname: str = Field(..., min_length=1)
    username: str = Field(..., min_length=1)
    email: EmailStr
    mobile: str = Field(..., min_length=10)
    country: str
    password: str = Field(..., min_length=6)


# valdating user inputs to get user info
class UserGet(BaseModel):
    id: Optional[str] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = None


class User(BaseModel):
    id: str
    firstname: str
    lastname: str
    username: str
    email: str
    mobile: str
    country: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class LoginSchema(BaseModel):
    username: str
    password: str


class LoginDisplay(BaseModel):
    user: UserDisplay
    access_token: str
    token_type: str


# Airport Codes Model
class AirportSearchData1(BaseModel):
    from_: str


class AirportSearchData2(BaseModel):
    to_: str


# Flight Search Model
class SearchFlight(BaseModel):
    sourceAirportCode: str
    destinationAirportCode: str
    date: str
    returnDate: Optional[str]
    itineraryType: str
    sortOrder: str
    numAdults: int
    numSeniors: int
    classOfService: str


class FlightDetail(BaseModel):
    airline: str
    sourceAirportCode: str
    destinationAirportCode: str
    departureDate: str
    classOfService: str
    flightNumber: str
    bookingReference: Optional[str]


class FavoriteFlight(BaseModel):
    outbound: FlightDetail
    returnFlight: Optional[FlightDetail] = None
    total_price: float


class SearchWeather(BaseModel):
    city: str


class Location(BaseModel):
    location: str


class LocInfo(BaseModel):
    title: str
    documentId: str
    secondaryText: str


class LocationSearchResponse(BaseModel):
    locs: list[LocInfo]


class HotelFilter(BaseModel):
    geoId: str
    checkIn: str
    checkOut: str


class HotelDetailsRequest(BaseModel):
    geoId: int
    checkIn: str
    checkOut: str
    adults: int


class Configuration(BaseModel):
    maxStayLength: int
    maxRooms: int
    maxChildrenPerRoom: int
    maxAdultsPerRoom: int


class DatePicker(BaseModel):
    configuration: Configuration
    lastSelectableDate: str
    timeZoneOffset: str


class FilterOption(BaseModel):
    name: str
    value: str


class FilterCategory(BaseModel):
    title: str
    name: str
    filters: Optional[List[FilterOption]] = None
    minValue: Optional[int] = None
    maxValue: Optional[int] = None
    selectedRangeStart: Optional[int] = None
    selectedRangeEnd: Optional[int] = None
    minDistance: Optional[int] = None
    maxDistance: Optional[int] = None
    locations: Optional[List[FilterOption]] = None


class HotelsFilterResponse(BaseModel):
    datePicker: DatePicker
    filters: List[FilterCategory]


class BubbleRating(BaseModel):
    count: str
    rating: float


class PhotoItemSizeDynamic(BaseModel):
    maxHeight: int
    maxWidth: int
    urlTemplate: HttpUrl


class PhotoItem(BaseModel):
    sizes: PhotoItemSizeDynamic


class HotelData(BaseModel):
    accomodation_id: Optional[str] = None
    accomodation: Optional[str] = None
    breakfast_info: Optional[str] = None
    accomodation_region: Optional[str] = None
    accomodation_rating: Optional[BubbleRating] = None
    accomodation_provider: Optional[str] = None
    priceForDisplay: Optional[str] = None
    strikethroughPrice: Optional[str] = None
    priceDetails: Optional[str] = None
    priceSummary: Optional[str] = None
    accomodation_photos: Optional[List[PhotoItem]] = None


class HotelDetails(BaseModel):
    id: str
    checkIn: str
    checkOut: Optional[str]


class Photo(BaseModel):
    maxHeight: Optional[int] = None
    maxWidth: Optional[int] = None
    urlTemplate: Optional[HttpUrl] = None

    class Config:
        json_encoders = {
            HttpUrl: lambda v: str(v),
        }


class LocalizedString(BaseModel):
    __typename: str
    text: str


class Price(BaseModel):
    displayPrice: Optional[str] = None
    strikeThroughPrice: Optional[LocalizedString] = None
    status: str
    providerName: str
    freeCancellation: Optional[str] = None
    pricingPeriod: Optional[str] = None


class Content(BaseModel):
    title: Optional[str] = None
    content: Optional[Union[str, List[str], List[dict]]] = None


class About(BaseModel):
    title: Optional[str] = None
    content: Optional[list[Content]] = None


class ReviewUser(BaseModel):
    deprecatedContributionCount: str
    avatar: Optional[Photo] = None


class Review(BaseModel):
    title: Optional[str] = None
    text: Optional[str] = None
    bubbleRatingText: Optional[str] = None
    publishedDate: Optional[str] = None
    userProfile: Optional[ReviewUser] = None
    photos: Optional[List[Photo]] = None


class Locations(BaseModel):
    title: Optional[str] = None
    address: str
    neighborhood: Optional[dict] = None
    gettingThere: Optional[dict] = None
    walkability: Optional[str] = None


class Restaurant(BaseModel):
    restaurant_name: Optional[str] = None
    bubbleRating: dict
    restauranttype: str
    distance: Optional[str] = None
    restaurantPhoto: Optional[Photo] = None


class Attraction(BaseModel):
    attraction_name: Optional[str] = None
    bubbleRating: dict
    primaryInfo: Optional[str]
    distance: Optional[str] = None
    attractionPhoto: Optional[Photo] = None


class ProfileImage(BaseModel):
    maxHeight: Optional[int] = None
    maxWidth: Optional[int] = None
    urlTemplate: Optional[HttpUrl] = None


class MemberProfile(BaseModel):
    profileImage: Optional[ProfileImage] = None


class TopAnswer(BaseModel):
    memberProfile: Optional[MemberProfile] = None


class QuestionAnswer(BaseModel):
    title: Optional[str] = None
    writtenDate: str
    memberProfile: Optional[MemberProfile] = None
    topAnswer: Optional[TopAnswer] = None


class AmenityDetail(BaseModel):
    title: Optional[str] = None
    content: Optional[List[str]] = None


class HotelDetailDisplay(BaseModel):
    photos: Optional[list[Photo]] = None
    accomodation_name: Optional[str] = None
    rating: float
    numberReviews: int
    rankingDetails: str
    price: Optional[Price] = None
    reviews: Optional[Review] = None
    location: Optional[Locations] = None
    restaurantsNearby: Optional[list[Restaurant]] = None
    attractionsNearby: Optional[list[Attraction]] = None
    qA: Optional[list[QuestionAnswer]] = None
    amenitiesScreen: Optional[List[AmenityDetail]] = None


class FlightDetails(BaseModel):
    airline_name: str = Field(..., alias="Airline Name")
    flight_number: int = Field(..., alias="Flight Number")
    departure_time: str = Field(..., alias="Departure Time")
    arrival_time: str = Field(..., alias="Arrival Time")
    duration: str = Field(..., alias="Duration")
    number_of_stops: int = Field(..., alias="Number of Stops")
    airline_logo: HttpUrl = Field(..., alias="Airline Logo")
    source_city_code: str = Field(..., alias="Source City Code")
    destination_city_code: str = Field(..., alias="Destination City Code")

    class Config:
        json_encoders = {
            HttpUrl: lambda v: str(v),
        }


class AccommodationPhoto(BaseModel):
    sizes: dict


class HotelsData(BaseModel):
    accomodation_id: str
    accomodation: str
    breakfast_info: str
    accomodation_region: str
    accomodation_rating: dict
    accomodation_provider: str
    priceForDisplay: str
    strikethroughPrice: Optional[str] = None
    priceDetails: str
    priceSummary: Optional[str] = None
    accomodation_photos: List[AccommodationPhoto]


class CartItem(BaseModel):
    outbound: Optional[FlightDetails] = None
    return_flight: Optional[FlightDetails] = None
    hotel: Optional[HotelsData] = None
    price: Optional[float] = None


class SaveForLater(BaseModel):
    user_email: str = Field(..., alias="userEmail")
    cart_items: list[CartItem] = Field(..., alias="cartItems")

    class Config:
        populate_by_name = True


class TourOfferDetail(BaseModel):
    url: Optional[str] = None
    price: Optional[str] = None
    rounded_up_price: Optional[str] = None
    offer_type: Optional[str] = None
    tour_title: Optional[str] = None
    partner: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    tour_category: Optional[str] = None


class PhotoUrls(BaseModel):
    small: Optional[HttpUrl]
    medium: Optional[HttpUrl]
    large: Optional[HttpUrl]
    original: Optional[HttpUrl]


class Booking(BaseModel):
    provider_name: Optional[str] = None
    url: Optional[HttpUrl] = None


class AnimalTag(BaseModel):
    tag: Optional[str] = None
    msg_header: Optional[str] = None
    msg_body: Optional[str] = None
    learn_more_text: Optional[str] = None
    education_portal_url: Optional[Union[str, HttpUrl]] = None


class AttractionData(BaseModel):
    location_id: str
    attraction_name: str
    attraction_reviews_count: int
    attraction_location: str
    attraction_photos: PhotoUrls
    attraction_raw_ranking: float
    attraction_rating: str
    attraction_description: str
    attraction_weburl: Optional[HttpUrl] = None
    attraction_category: List[str]
    attraction_phone: Optional[str] = None
    attraction_website: Optional[HttpUrl] = None
    attraction_address: Optional[str] = None
    attraction_subtype: List[str]
    attraction_offer_tours: List[TourOfferDetail]
    attraction_booking: Optional[Booking] = None
    attraction_animal_tag: Optional[AnimalTag] = None


class AttractionRequest(BaseModel):
    location_id: str
    language: str
    currency: str


class SearchOneWayFlight(BaseModel):
    sourceAirportCode: str
    destinationAirportCode: str
    date: str
    itineraryType: str
    sortOrder: str
    numAdults: int
    numSeniors: int
    classOfService: str
