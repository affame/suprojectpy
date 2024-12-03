import requests

BASE_URL = "https://api.open-meteo.com/v1/forecast"

def get_weather_data(latitude, longitude):
    """
    Запрашивает данные о погоде из Open-Meteo API.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": True
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Ошибка API: {response.status_code} - {response.text}")

def parse_weather_data(raw_data):
    """
    Преобразует "сырые" данные из API в удобный формат.
    """
    current_weather = raw_data.get("current_weather", {})
    hourly_data = raw_data.get("hourly", {})

    # Извлекаем данные текущей погоды и первых доступных значений
    return {
        "temperature": current_weather.get("temperature"),
        "humidity": hourly_data.get("relative_humidity_2m", [None])[0],  # Первое значение влажности
        "wind_speed": current_weather.get("windspeed"),
        "precipitation_probability": hourly_data.get("precipitation_probability", [None])[0]  # Первое значение вероятности дождя
    }

