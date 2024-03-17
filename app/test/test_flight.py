import pytest
import responses
from fastapi.testclient import TestClient
from app.main import app  # Adjust the import path as needed

client = TestClient(app)


@pytest.fixture
def flight_search_data():
    return {
        "sourceAirportCode": "DEL",
        "destinationAirportCode": "BOM",
        "date": "2023-05-01",
        "returnDate": "2023-05-10",
        "itineraryType": "roundTrip",
        "sortOrder": "price",
        "numAdults": 1,
        "numSeniors": 0,
        "classOfService": "economy",
    }


@responses.activate
def test_search_round_trip_flight_success(flight_search_data):
    responses.add(
        responses.GET,
        "https://tripadvisor16.p.rapidapi.com/api/v1/flights/searchFlights",
        json={"data": {"flights": []}},
        status=200,
    )

    response = client.post("/user/search-round-trip-flights/", json=flight_search_data)
    assert response.status_code == 200
