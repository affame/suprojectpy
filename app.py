from flask import Flask, render_template, request
from services.weather import get_weather_data, parse_weather_data
from services.model import check_bad_weather
from services.geo import get_coordinates

app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            # Получение названий городов из формы
            start_city = request.form.get("start_city")
            end_city = request.form.get("end_city")

            # Получение координат по названию городов
            start_lat, start_lon = get_coordinates(start_city)
            end_lat, end_lon = get_coordinates(end_city)

            # Получение данных из API для обеих точек
            start_raw_weather = get_weather_data(start_lat, start_lon)
            end_raw_weather = get_weather_data(end_lat, end_lon)

            # Парсинг данных
            start_weather = parse_weather_data(start_raw_weather)
            end_weather = parse_weather_data(end_raw_weather)

            # Анализ погоды
            start_result = check_bad_weather(start_weather)
            end_result = check_bad_weather(end_weather)

            # Передача данных в шаблон
            return render_template(
                "result.html",
                start_city=start_city,  # Название начального города
                end_city=end_city,      # Название конечного города
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
