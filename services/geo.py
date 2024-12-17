import ssl
import certifi
from geopy.geocoders import Nominatim

# Настройка SSL-контекста с использованием certifi
ctx = ssl.create_default_context(cafile=certifi.where())

def get_coordinates(city_name):
    geolocator = Nominatim(user_agent="weather_app", ssl_context=ctx)
    location = geolocator.geocode(city_name, language="ru")
    if location:
        return location.latitude, location.longitude
    else:
        raise ValueError(f"Город '{city_name}' не найден.")

print(get_coordinates("Москва"))

