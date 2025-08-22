import os
import pytest
from fastapi.testclient import TestClient

from weatherapp.main import app

client = TestClient(app)

def test_weather_statistics_endpoint():
    """Check that the endpoint returns data with required keys"""
    response = client.get("/weather/statistics", params={
        "city": "Moscow",
        "start_date": "2023-07-01",
        "end_date": "2023-07-02"
    })
    assert response.status_code == 200
    json_data = response.json()
    assert "data" in json_data
    assert isinstance(json_data["data"], list)
    if json_data["data"]:
        first = json_data["data"][0]
        for key in ["date", "avg_temp", "precipitation_mm", "is_sunny"]:
            assert key in first

def test_weather_statistics_cache():
    """Second call should return cached=True"""
    first = client.get("/weather/statistics", params={
        "city": "Moscow",
        "start_date": "2023-07-01",
        "end_date": "2023-07-02"
    }).json()
    second = client.get("/weather/statistics", params={
        "city": "Moscow",
        "start_date": "2023-07-01",
        "end_date": "2023-07-02"
    }).json()
    assert second.get("cached") is True
