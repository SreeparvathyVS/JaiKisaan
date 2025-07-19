# tools/api_tools.py

from google.adk.tools import tool
import requests
import datetime

@tool
def fetch_price_data(crop_name: str, location: str) -> dict:
    # Simulated API logic
    # Replace with real Agmarknet or FPO API
    return {
        "crop": crop_name,
        "location": location,
        "latest_prices": [
            {"mandi": "Lasalgaon", "min": 1200, "max": 1500, "modal": 1350}
        ],
        "history": [
            {"date": "2025-07-10", "price": 1250},
            {"date": "2025-07-11", "price": 1275},
            {"date": "2025-07-12", "price": 1300},
        ]
    }

@tool
def fetch_weather_data(crop: str, location: str) -> dict:
    """
    Fetch simple 7-day weather forecast for a given location.
    No analysis or advice—just raw data like temp, rain, humidity.
    """
    # Simulated static forecast (you can replace with actual OpenWeatherMap API logic)
    today = datetime.date.today()
    forecast = []

    for i in range(7):
        day = today + datetime.timedelta(days=i)
        forecast.append({
            "date": str(day),
            "temperature": f"{30 + i % 3}°C",
            "rainfall_mm": round(5.0 + i * 0.8, 1),
            "humidity_percent": 60 + (i % 5)
        })

    return {
        "location": location,
        "forecast": forecast
    }