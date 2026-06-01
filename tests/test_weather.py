
from unittest.mock import patch
from app.models.schemas import WeatherResponse


MOCK_WEATHER = WeatherResponse(
    city="London",
    description="Sunny",
    temperature_c=22.0,
    humidity=60,
    wind_kmh=15.0,
)


def test_weather_success(client, auth_headers):
    with patch("app.api.weather.httpx.Client") as mock_client_cls:
        mock_resp = mock_client_cls.return_value.__enter__.return_value.get.return_value
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {
            "current_condition": [{
                "weatherDesc": [{"value": "Sunny"}],
                "temp_C": "22",
                "humidity": "60",
                "windspeedKmph": "15",
            }]
        }
        response = client.get("/weather", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "London"
    assert data["temperature_c"] == 22.0
    assert data["description"] == "Sunny"


def test_weather_requires_auth(client):
    response = client.get("/weather")
    assert response.status_code == 401