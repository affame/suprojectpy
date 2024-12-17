from flask import Flask, request, render_template
from services.geo import get_coordinates  # Импорт функции для геокодинга
from services.weather import get_weather_data, parse_weather_data  # Импорт функций для погоды
from services.model import check_bad_weather  # Импорт логики анализа погоды

app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            # Получаем названия городов из формы
            start_city = request.form.get("start_city")
            end_city = request.form.get("end_city")

            # Конвертируем названия городов в координаты
            start_lat, start_lon = get_coordinates(start_city)
            end_lat, end_lon = get_coordinates(end_city)

            # Получаем данные о погоде для обеих точек
            start_raw_weather = get_weather_data(start_lat, start_lon)
            end_raw_weather = get_weather_data(end_lat, end_lon)

            # Парсинг полученных данных о погоде
            start_weather = parse_weather_data(start_raw_weather)
            end_weather = parse_weather_data(end_raw_weather)

            # Анализ погоды с использованием логики из model.py
            start_result = check_bad_weather(start_weather)
            end_result = check_bad_weather(end_weather)

            # Передача данных в шаблон result.html
            return render_template(
                "result.html",
                start_weather=start_weather,
                start_result=start_result,
                end_weather=end_weather,
                end_result=end_result
            )
        except Exception as e:
            # Обработка ошибок и вывод их на отдельной странице
            return render_template("error.html", error=str(e)), 500

    # При GET-запросе отобразить главную страницу с формой
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
