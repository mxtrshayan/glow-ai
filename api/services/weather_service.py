# api/services/weather_service.py
# ── WeatherAPI.com integration ────────────────────────────────
import httpx
from api.config import WEATHER_API_KEY

WEATHER_API_BASE = "https://api.weatherapi.com/v1"


async def get_weather(lat: float, lon: float) -> dict:
    """
    Fetch current weather from weatherapi.com for the given coordinates.
    Returns a simplified dict with condition, temp_c, humidity, and a
    makeup-relevant weather_category (hot/humid/cold/rainy/mild).
    """
    if not WEATHER_API_KEY:
        return {"error": "WEATHER_API_KEY not configured"}

    url = f"{WEATHER_API_BASE}/current.json"
    params = {"key": WEATHER_API_KEY, "q": f"{lat},{lon}", "aqi": "no"}

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            raw = resp.json()

        current = raw["current"]
        location = raw["location"]
        condition_text: str = current["condition"]["text"]
        temp_c: float = current["temp_c"]
        humidity: int = current["humidity"]
        icon_url: str = "https:" + current["condition"]["icon"]

        # Derive makeup-relevant category
        lower = condition_text.lower()
        if any(w in lower for w in ["rain", "drizzle", "shower", "thunder", "snow", "sleet"]):
            category = "rainy"
        elif temp_c >= 35 or humidity >= 80:
            category = "hot_humid"
        elif temp_c <= 12:
            category = "cold"
        else:
            category = "mild"

        return {
            "city": location.get("name", ""),
            "country": location.get("country", ""),
            "condition": condition_text,
            "temp_c": temp_c,
            "humidity": humidity,
            "icon_url": icon_url,
            "category": category,        # used by prompt builder
        }

    except httpx.HTTPStatusError as e:
        return {"error": f"Weather API error: {e.response.status_code}"}
    except Exception as e:
        return {"error": str(e)}
