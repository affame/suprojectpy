from flask import Flask, render_template, request
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from services.weather import get_weather_data, parse_weather_data
from services.model import check_bad_weather  # Импортируем функцию из model.py

app = Flask(__name__)
geolocator = Nominatim(user_agent="weather_app")

def get_city_coordinates(city_name):
    try:
        # Получаем координаты города
        location = geolocator.geocode(city_name)
        if location:
            return location.latitude, location.longitude
        else:
            raise ValueError(f"Город '{city_name}' не найден. Возможно, это опечатка или некорректное название.")
    except GeocoderTimedOut:
        raise ValueError("Сервис геокодирования не отвечает. Попробуйте позже.")
    except GeocoderServiceError:
        raise ValueError("Ошибка сервиса геокодирования. Попробуйте позже.")
    except Exception as e:
        raise ValueError(f"Ошибка при обработке города: {str(e)}")

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            # Получаем названия городов
            start_city = request.form.get("start_city")
            end_city = request.form.get("end_city")

            # Проверка на совпадение городов
            if start_city.lower() == end_city.lower():
                return render_template("error.html", error="Начальный и конечный города не могут быть одинаковыми! Пожалуйста, введите разные города.")

            # Получаем координаты для обоих городов
            start_lat, start_lon = get_city_coordinates(start_city)
            end_lat, end_lon = get_city_coordinates(end_city)

            # Получаем данные о погоде для обоих городов
            start_raw_weather = get_weather_data(start_lat, start_lon)
            end_raw_weather = get_weather_data(end_lat, end_lon)

            # Парсим данные погоды
            start_weather = parse_weather_data(start_raw_weather)
            end_weather = parse_weather_data(end_raw_weather)

            # Анализируем погоду
            start_result = check_bad_weather(start_weather)  # Вызываем функцию из model.py
            end_result = check_bad_weather(end_weather)  # Вызываем функцию из model.py

            # Передаем данные в шаблон
            return render_template(
                "result.html", 
                start_weather=start_weather,
                start_result=start_result,
                start_city=start_city,  # Передаем город для отображения
                end_weather=end_weather,
                end_result=end_result,
                end_city=end_city  # Передаем город для отображения
            )
        except ValueError as e:
            return render_template("error.html", error=str(e)), 400
        except Exception as e:
            return render_template("error.html", error="Произошла ошибка: " + str(e)), 500

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
