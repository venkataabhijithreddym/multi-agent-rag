import httpx
from fastapi import APIRouter, Depends, HTTPException
from app.auth.dependencies import get_current_user
from app.database import User
from app.models.schemas import WeatherResponse
from app.config import get_settings

router = APIRouter(tags=["weather"])
settings = get_settings()


@router.get("/weather", response_model=WeatherResponse)
def weather(city: str = None, current_user: User = Depends(get_current_user)):
    city = (city or settings.weather_city).strip()
    url = f"https://wttr.in/{city}?format=j1"
    try:
        with httpx.Client(timeout=10) as client:
            resp = client.get(url)
            resp.raise_for_status()
            data = resp.json()
        current = data["current_condition"][0]
        return WeatherResponse(
            city=city,
            description=current["weatherDesc"][0]["value"],
            temperature_c=float(current["temp_C"]),
            humidity=int(current["humidity"]),
            wind_kmh=float(current["windspeedKmph"]),
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Weather service error: {e}")