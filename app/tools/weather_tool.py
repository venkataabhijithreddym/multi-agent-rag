

import httpx
from langchain_core.tools import tool
from app.config import get_settings

settings = get_settings()


def _fetch_weather(city: str) -> dict:
    url = f"https://wttr.in/{city}?format=j1"
    with httpx.Client(timeout=10) as client:
        resp = client.get(url)
        resp.raise_for_status()
        data = resp.json()

    current = data["current_condition"][0]
    return {
        "city": city,
        "description": current["weatherDesc"][0]["value"],
        "temperature_c": float(current["temp_C"]),
        "humidity": int(current["humidity"]),
        "wind_kmh": float(current["windspeedKmph"]),
    }


@tool
def get_weather(city: str = "") -> str:
    """Get current weather for a city. If no city provided, uses the configured default city."""
    target = city.strip() if city.strip() else settings.weather_city
    try:
        w = _fetch_weather(target)
        return (
            f"Weather in {w['city']}: {w['description']}, "
            f"{w['temperature_c']}°C, humidity {w['humidity']}%, "
            f"wind {w['wind_kmh']} km/h."
        )
    except Exception as e:
        return f"Could not fetch weather for '{target}': {e}"