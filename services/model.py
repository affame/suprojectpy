def check_bad_weather(weather): #Функция для определения плохой погоды
    temperature = weather.get("temperature")
    wind_speed = weather.get("wind_speed")
    precipitation_probability = weather.get("precipitation_probability")
    humidity = weather.get("humidity")

    #Проверка на отсутствие данных
    if temperature is None or wind_speed is None or precipitation_probability is None or humidity is None:
        return "Ошибка: не удалось получить полные данные о погоде."

    #Логика определения плохой погоды
    if temperature < 0 or temperature > 35:
        return "Плохая погода: экстремальная температура"
    if wind_speed > 50:
        return "Плохая погода: сильный ветер"
    if precipitation_probability > 70:
        return "Плохая погода: высокая вероятность дождя"
    if humidity > 80:
        return "Плохая погода: высокая влажность"

    #Если все условия не выполнены, погода считается хорошей
    return "Клевая погода"

