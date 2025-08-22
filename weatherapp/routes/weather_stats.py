from fastapi import APIRouter, Query
from datetime import datetime, timedelta
import os
import json
import time
import requests

router = APIRouter(prefix="/weather", tags=["weather-statistics"])

API_KEY = os.getenv("VISUAL_CROSSING_API_KEY")

BASE_URL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"
CACHE_FILE = "statistics_cache.json"
CACHE_TTL = 3600  # 1 hour in seconds

# --- helper: load and save cache ---
def load_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def is_cache_valid(entry_timestamp):
    return time.time() - entry_timestamp < CACHE_TTL

@router.get("/statistics")
def weather_statistics(
    city: str = Query(..., description="City"),
    start_date: str = Query(..., description="Start date in yyyy-MM-dd"),
    end_date: str = Query(..., description="End date in yyyy-MM-dd")
):
    """Return daily weather statistics between two dates with caching."""
    # validate dates
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        if end_dt < start_dt:
            return {"error": "end_date must be after start_date"}
    except ValueError:
        return {"error": "Invalid date format. Use yyyy-MM-dd"}

    cache = load_cache()
    cache_key = f"{city}_{start_date}_{end_date}"

    # return cached result if still valid
    if cache_key in cache and is_cache_valid(cache[cache_key]["ts"]):
        return {"cached": True, "data": cache[cache_key]["data"]}

    # call Visual Crossing API
    url = f"{BASE_URL}/{city}/{start_date}/{end_date}"
    params = {
        "unitGroup": "metric",
        "key": API_KEY,
        "lang": "ru",
        "include": "days"
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        days = resp.json().get("days", [])
    except Exception as e:
        return {"error": str(e)}

    SUNNY_KEYWORDS = {"clear", "sunny", "mostly clear", "partly sunny", "mainly clear"}
    result = []
    for d in days:
        conditions = d.get("conditions", "").lower()
        is_sunny = any(k in conditions for k in SUNNY_KEYWORDS)
        result.append({
            "date": d.get("datetime"),
            "avg_temp": d.get("temp"),
            "precipitation_mm": d.get("precip", 0.0),
            "is_sunny": is_sunny
        })

    # save to cache
    cache[cache_key] = {"ts": time.time(), "data": result}
    save_cache(cache)

    return {"cached": False, "data": result}
