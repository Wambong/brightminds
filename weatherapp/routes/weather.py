from fastapi import APIRouter, Query
from datetime import datetime
import requests
import os

router = APIRouter(prefix="/weather", tags=["weather"])

API_KEY = os.getenv("VISUAL_CROSSING_API_KEY")

BASE_URL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"

# Условия, которые считаем "солнечными"
SUNNY_KEYWORDS = {"clear", "sunny", "mostly clear", "partly sunny", "mainly clear"}

import time


def get_with_retries(url, params, retries=3, delay=2):
    for attempt in range(retries):
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            return resp
        except requests.exceptions.RequestException as e:
            if attempt == retries - 1:
                raise e
            time.sleep(delay)


@router.get("/is_sunny")
def is_sunny(
        city: str = Query("Москва", description="Город"),
        date: str = Query(..., description="Дата в формате ГГГГ.ММ.ДД")
):
    """Проверяет, была ли солнечная погода в указанном городе в указанную дату"""

    # Проверяем дату
    try:
        dt_parsed = datetime.strptime(date, "%Y.%m.%d")
        date_str = dt_parsed.strftime("%Y-%m-%d")  # формат для API
    except ValueError:
        return {"error": "Неверный формат даты. Используйте ГГГГ.ММ.ДД."}

    url = f"{BASE_URL}/{city}/{date_str}"
    params = {
        "unitGroup": "metric",
        "key": API_KEY,
        "lang": "ru",
        "include": "days"
    }

    try:
        resp = get_with_retries(url, params)
        resp.raise_for_status()
        data = resp.json()
        conditions = data["days"][0].get("conditions", "").lower()
        is_sunny = any(keyword in conditions for keyword in SUNNY_KEYWORDS)
        return {
            "city": city,
            "date": date,
            "sunny": is_sunny,
            "description": conditions
        }
    except Exception as e:
        return {
            "city": city,
            "date": date,
            "sunny": None,
            "error": str(e)
        }


@router.get("/precipitation")
def get_precipitation(
        city: str = Query("Москва", description="Город"),
        date: str = Query(..., description="Дата в формате ГГГГ.ММ.ДД")
):
    """Возвращает количество осадков в мм за указанную дату (или null, если их не было)"""

    # Проверяем дату
    try:
        dt_parsed = datetime.strptime(date, "%Y.%m.%d")
        date_str = dt_parsed.strftime("%Y-%m-%d")
    except ValueError:
        return {"error": "Неверный формат даты. Используйте ГГГГ.ММ.ДД."}

    url = f"{BASE_URL}/{city}/{date_str}"
    params = {
        "unitGroup": "metric",
        "key": API_KEY,
        "lang": "ru",
        "include": "days"
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        day_data = data["days"][0]
        precipitation = day_data.get("precip", 0.0)
        return {
            "city": city,
            "date": date,
            "precipitation": None if precipitation == 0 else precipitation
        }
    except Exception as e:
        return {
            "city": city,
            "date": date,
            "precipitation": None,
            "error": str(e)
        }


@router.get("/temperature")
def get_temperature(
        city: str = Query("Москва", description="Город"),
        date: str = Query(..., description="Дата в формате ГГГГ.ММ.ДД")
):
    """Возвращает среднюю температуру воздуха (°C) за указанный день"""
    try:
        dt_parsed = datetime.strptime(date, "%Y.%m.%d")
        date_str = dt_parsed.strftime("%Y-%m-%d")
    except ValueError:
        return {"error": "Неверный формат даты. Используйте ГГГГ.ММ.ДД."}

    url = f"{BASE_URL}/{city}/{date_str}"
    params = {
        "unitGroup": "metric",
        "key": API_KEY,
        "lang": "ru",
        "include": "days"
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        day_data = resp.json()["days"][0]
        avg_temp = day_data.get("temp", None)
        return {
            "city": city,
            "date": date,
            "temperature_c": avg_temp
        }
    except Exception as e:
        return {
            "city": city,
            "date": date,
            "temperature_c": None,
            "error": str(e)
        }
