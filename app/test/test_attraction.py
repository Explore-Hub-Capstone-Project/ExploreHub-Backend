import pytest
import responses
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture
def attraction_search_data_success():
    return {
        "location_id": "304554",
        "language": "en_US",
        "currency": "USD",
    }


@responses.activate
def test_search_attractions_success(attraction_search_data_success):
    responses.add(
        responses.POST,
        "https://tourist-attraction.p.rapidapi.com/search",
        json={"results": {"data": []}},
        status=200,
    )

    response = client.post(
        "/attraction/search-attractions", json=attraction_search_data_success
    )
    assert response.status_code == 200


@pytest.fixture
def attraction_search_data_failure():
    return {
        "location_id": "11",
        "language": "en_US",
        "currency": "USD",
    }


@responses.activate
def test_search_attractions_failure(attraction_search_data_failure):
    responses.add(
        responses.POST,
        "https://tourist-attraction.p.rapidapi.com/search",
        json={"results": {"data": []}},
        status=500,
    )

    response = client.post(
        "/attraction/search-attractions", json=attraction_search_data_failure
    )
    assert response.status_code != 200
