import requests

YANDEX_API_KEY = ""  
YANDEX_GEOCODER_URL = "https://geocode-maps.yandex.ru/1.x/"

def get_coordinates(city_name):
    try:
        params = {
            "apikey": YANDEX_API_KEY,
            "geocode": city_name,
            "format": "json",
        }
        response = requests.get(YANDEX_GEOCODER_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        geo_object = (
            data.get("response", {})
            .get("GeoObjectCollection", {})
            .get("featureMember", [{}])[0]
            .get("GeoObject", {})
        )
        
        if not geo_object:
            raise ValueError(f"Город '{city_name}' не найден. Проверьте правильность написания.")
        
        # Извлекаем координаты
        coordinates = geo_object.get("Point", {}).get("pos", "")
        if not coordinates:
            raise ValueError(f"Не удалось получить координаты для города '{city_name}'.")
        
        lon, lat = map(float, coordinates.split(" "))
        return lat, lon
    except requests.RequestException as e:
        raise ValueError(f"Ошибка подключения к Яндекс API: {str(e)}")
    except Exception as e:
        raise ValueError(f"Ошибка при обработке города '{city_name}': {str(e)}")
