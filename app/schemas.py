from pydantic import BaseModel, EmailStr, Field, HttpUrl
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
    checkOut: str


class Photo(BaseModel):
    maxHeight: Optional[int] = None
    maxWidth: Optional[int] = None
    urlTemplate: Optional[HttpUrl] = None


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


class AttractionsMain(BaseModel):
    location_id: str
    language: str
    currency: str
