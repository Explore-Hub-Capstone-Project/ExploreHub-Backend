import pytest
import responses
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture
def flight_search_data_success():
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
def test_search_round_trip_flight_success(flight_search_data_success):
    responses.add(
        responses.GET,
        "https://tripadvisor16.p.rapidapi.com/api/v1/flights/searchFlights",
        json={"data": {"flights": []}},
        status=200,
    )

    response = client.post(
        "/user/search-round-trip-flights/", json=flight_search_data_success
    )
    assert response.status_code == 200


@pytest.fixture
def flight_search_data_failure():
    return {
        "sourceAirportCode": "XXX",
        "destinationAirportCode": "XXX",
        "date": "2023-05-01",
        "returnDate": "2023-05-10",
        "itineraryType": "roundTrip",
        "sortOrder": "price",
        "numAdults": 1,
        "numSeniors": 0,
        "classOfService": "economy",
    }


@responses.activate
def test_search_round_trip_flight_failure(flight_search_data_failure):
    responses.add(
        responses.GET,
        "https://tripadvisor16.p.rapidapi.com/api/v1/flights/searchFlights",
        json={"data": {"flights": []}},
        status=500,
    )

    response = client.post(
        "/user/search-round-trip-flights/", json=flight_search_data_failure
    )
    assert response.status_code != 200


@pytest.fixture
def airport_search_data_from_success():
    return {"from_": "JFK"}


@responses.activate
def test_search_from_airport_success(airport_search_data_from_success):
    mock_response_data = {
        "data": [
            {
                "details": {
                    "parent_ids": ["1234"],
                },
                "airportCode": "JFK",
            }
        ]
    }
    responses.add(
        responses.GET,
        "https://tripadvisor16.p.rapidapi.com/api/v1/flights/searchAirport",
        json=mock_response_data,
        status=200,
    )

    response = client.post(
        "/user/search-from-airport/", json=airport_search_data_from_success
    )
    assert response.status_code == 200


@pytest.fixture
def airport_search_data_from_failure():
    return {"from_": "XXX"}


@responses.activate
def test_search_from_airport_failure(airport_search_data_from_failure):
    mock_response_data = {
        "data": [
            {
                "details": {
                    "parent_ids": ["1234"],
                },
                "airportCode": "JFK",
            }
        ]
    }
    responses.add(
        responses.GET,
        "https://tripadvisor16.p.rapidapi.com/api/v1/flights/searchAirport",
        json=mock_response_data,
        status=400,
    )

    response = client.post(
        "/user/search-from-airport/", json=airport_search_data_from_failure
    )
    assert response.status_code != 200


@pytest.fixture
def airport_search_data_to_success():
    return {"to_": "JFK"}


@responses.activate
def test_search_to_airport_success(airport_search_data_to_success):
    mock_response_data = {
        "data": [
            {
                "details": {
                    "parent_ids": ["1234"],
                },
                "airportCode": "JFK",
            }
        ]
    }
    responses.add(
        responses.GET,
        "https://tripadvisor16.p.rapidapi.com/api/v1/flights/searchAirport",
        json=mock_response_data,
        status=200,
    )

    response = client.post(
        "/user/search-to-airport/", json=airport_search_data_to_success
    )
    assert response.status_code == 200


@pytest.fixture
def airport_search_data_to_failure():
    return {"to_": "XXX"}


@responses.activate
def test_search_to_airport_failure(airport_search_data_to_failure):
    mock_response_data = {
        "data": [
            {
                "details": {
                    "parent_ids": ["1234"],
                },
                "airportCode": "JFK",
            }
        ]
    }
    responses.add(
        responses.GET,
        "https://tripadvisor16.p.rapidapi.com/api/v1/flights/searchAirport",
        json=mock_response_data,
        status=400,
    )

    response = client.post(
        "/user/search-to-airport/", json=airport_search_data_to_failure
    )
    assert response.status_code != 200
