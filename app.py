from flask import Flask, render_template, request
from services.weather import get_weather_data, parse_weather_data
from services.yandex_geo import get_coordinates
from services.model import check_bad_weather

app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            # Получаем данные из формы
            start_city = request.form.get("start_city").strip()
            end_city = request.form.get("end_city").strip()
            days = int(request.form.get("days"))
            intermediate_cities = [
                city.strip() for city in request.form.getlist("intermediate_cities") if city.strip()
            ]

            # Проверяем ввод
            if start_city.lower() == end_city.lower():
                raise ValueError("Начальный и конечный города не должны совпадать!")

            cities = [{"name": start_city}, {"name": end_city}]
            for city in intermediate_cities:
                cities.insert(-1, {"name": city})

            # Получение данных для всех точек маршрута
            for city in cities:
                try:
                    lat, lon = get_coordinates(city["name"])
                    city["lat"] = lat
                    city["lon"] = lon
                    city["forecast"] = parse_weather_data(get_weather_data(lat, lon, days))
                except Exception as e:
                    raise ValueError(f"Ошибка для города '{city['name']}': {str(e)}")

            return render_template(
                "result.html",
                cities=cities,
                days=days
            )
        except Exception as e:
            return render_template("error.html", error=str(e)), 500
    return render_template("index.html")
    
if __name__ == "__main__":
    app.run(debug=True)
