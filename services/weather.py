import requests

BASE_URL = "https://api.open-meteo.com/v1/forecast"

def get_weather_data(latitude, longitude):
    base_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": True,  # Запрос текущей погоды
        "hourly": "relative_humidity_2m,precipitation_probability",  # Включаем hourly данные
    }
    response = requests.get(base_url, params=params)
    
    if response.status_code != 200:
        raise Exception(f"Ошибка API: {response.status_code} - {response.text}")
    
    return response.json()


def parse_weather_data(raw_data):
    """
    Преобразует "сырые" данные из API в удобный формат.
    """
    current_weather = raw_data.get("current_weather", {})
    hourly_data = raw_data.get("hourly", {})

    # Определяем текущий час
    humidity = hourly_data.get("relative_humidity_2m", [None])[0]  # Первый час
    precipitation_probability = hourly_data.get("precipitation_probability", [None])[0]

    return {
        "temperature": current_weather.get("temperature"),
        "humidity": humidity,  # Влажность из hourly
        "wind_speed": current_weather.get("windspeed"),
        "precipitation_probability": precipitation_probability,  # Вероятность дождя из hourly
    }



