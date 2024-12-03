from flask import Flask, render_template, request
from services.weather import get_weather_data, parse_weather_data
from services.model import check_bad_weather

app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            # Получение координат начальной и конечной точек
            start_lat = request.form.get("start_lat", type=float)
            start_lon = request.form.get("start_lon", type=float)
            end_lat = request.form.get("end_lat", type=float)
            end_lon = request.form.get("end_lon", type=float)
            
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
