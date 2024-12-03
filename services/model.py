def check_bad_weather(weather):
    if weather["temperature"] < 0 or weather["temperature"] > 35:
        return "Плохая погода (экстремальная температура)"
    if weather["wind_speed"] > 50:
        return "Плохая погода (сильный ветер)"
    if weather["precipitation_probability"] > 70:
        return "Плохая погода (высокая вероятность осадков)"
    return "Хорошая погода"
