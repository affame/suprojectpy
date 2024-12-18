from flask import Flask, render_template, request
from services.weather import get_weather_data, parse_weather_data
from services.yandex_geo import get_coordinates
from services.model import check_bad_weather

app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            # Получаем названия городов
            start_city = request.form.get("start_city").strip()
            end_city = request.form.get("end_city").strip()

            # Проверяем, что начальный и конечный города не совпадают
            if start_city.lower() == end_city.lower():
                raise ValueError("Начальный и конечный города не должны совпадать!")

            # Преобразуем города в координаты через Яндекс Геокодер
            try:
                start_lat, start_lon = get_coordinates(start_city)
            except Exception as e:
                raise ValueError(f"Ошибка для города '{start_city}': {str(e)}")

            try:
                end_lat, end_lon = get_coordinates(end_city)
            except Exception as e:
                raise ValueError(f"Ошибка для города '{end_city}': {str(e)}")

            # Получаем данные о погоде
            start_raw_weather = get_weather_data(start_lat, start_lon)
            end_raw_weather = get_weather_data(end_lat, end_lon)

            # Парсим и анализируем данные
            start_weather = parse_weather_data(start_raw_weather)
            end_weather = parse_weather_data(end_raw_weather)
            start_result = check_bad_weather(start_weather)
            end_result = check_bad_weather(end_weather)

            # Передаем данные в шаблон
            return render_template(
                "result.html",
                start_city=start_city,
                end_city=end_city,
                start_weather=start_weather,
                start_result=start_result,
                end_weather=end_weather,
                end_result=end_result
            )
        except Exception as e:
            return render_template("error.html", error=str(e)), 500
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
