import pytest
import responses
from fastapi.testclient import TestClient
from app.main import app
import re

client = TestClient(app)


@pytest.fixture
def weather_search_data():
    return {"city": "Mumbai"}


@responses.activate
def test_get_weather_success(weather_search_data):
    url_regex = re.compile(
        r"http://api.openweathermap.org/data/2.5/weather\?q=.*&appid=.*"
    )
    responses.add(
        responses.GET,
        url_regex,
        json={
            "main": {
                "temp": 300.15,
                "feels_like": 304.15,
                "humidity": 44,
            },
            "weather": [
                {
                    "main": "Clear",
                }
            ],
        },
        status=200,
    )

    response = client.post("/user/get-weather/", json=weather_search_data)
    assert response.status_code == 200
    assert response.json()[0]["Description"] == "Clear"
