from flask import Flask, render_template, request
from services.weather import get_weather_data, parse_weather_data
from services.model import check_bad_weather

app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            latitude = request.form.get("latitude", type=float)
            longitude = request.form.get("longitude", type=float)
            
            # Получение и обработка данных из API
            raw_weather_data = get_weather_data(latitude, longitude)
            weather = parse_weather_data(raw_weather_data)
            
            # Анализ погоды
            result = check_bad_weather(weather)
            print(weather)  # Добавьте это в app.py перед передачей данных в шаблон

            return render_template("result.html", weather=weather, result=result)
        except Exception as e:
            return f"Ошибка: {e}", 500
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
