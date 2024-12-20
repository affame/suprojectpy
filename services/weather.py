import requests

BASE_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather_data(latitude, longitude, days=1):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max",
        "timezone": "auto",
        "forecast_days": days,
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
    except requests.RequestException as e:
        raise Exception(f"Ошибка подключения к API: {e}")
    
    data = response.json()
    if not data:
        raise Exception("Данные API недоступны или некорректны.")
    
    return data

def parse_weather_data(raw_data):
    daily_data = raw_data.get("daily", {})
    days = len(daily_data.get("temperature_2m_max", []))

    forecast = []
    for i in range(days):
        forecast.append({
            "date": daily_data.get("time", [])[i],
            "max_temperature": daily_data.get("temperature_2m_max", [None])[i],
            "min_temperature": daily_data.get("temperature_2m_min", [None])[i],
            "precipitation_sum": daily_data.get("precipitation_sum", [None])[i],
            "wind_speed_max": daily_data.get("windspeed_10m_max", [None])[i],
            "latitude": daily_data.get("latitude", 0),  
            "longitude": daily_data.get("longitude", 0), 
        })
    return forecast



