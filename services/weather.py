import requests
from config import API_KEY, BASE_URL

def get_weather_data(latitude, longitude):
    # Получение locationKey по координатам
    location_url = f"{BASE_URL}locations/v1/cities/geoposition/search"
    params = {
        "apikey": API_KEY,
        "q": f"{latitude},{longitude}"
    }
    response = requests.get(location_url, params=params)
    response.raise_for_status()
    location_key = response.json()["Key"]

    # Получение данных о погоде
    weather_url = f"{BASE_URL}currentconditions/v1/{location_key}"
    weather_response = requests.get(weather_url, params={"apikey": API_KEY})
    weather_response.raise_for_status()
    return weather_response.json()[0]

def parse_weather_data(data):
    return {
        "temperature": data["Temperature"]["Metric"]["Value"],  # В градусах Цельсия
        "humidity": data.get("RelativeHumidity"),               # Влажность в процентах
        "wind_speed": data["Wind"]["Speed"]["Metric"]["Value"], # Скорость ветра в км/ч
        "precipitation_probability": data.get("PrecipitationProbability", 0)  # Вероятность осадков
    }
