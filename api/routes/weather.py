# api/routes/weather.py
# ── Weather route ─────────────────────────────────────────────
from fastapi import APIRouter, Query
from api.services.weather_service import get_weather

router = APIRouter()


@router.get("/weather")
async def weather_endpoint(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
):
    """Return current weather data for given coordinates."""
    return await get_weather(lat, lon)
