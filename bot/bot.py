import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio

BOT_TOKEN = "8099087032:AAG2ngeN2ap7yyf1uI-y-y2cwrHHOCTu5Sw"
YANDEX_API_KEY = "67c3277c-91e1-4fdf-8a33-b8fec2870325"

BASE_URL = "https://api.open-meteo.com/v1/forecast"
YANDEX_GEOCODER_URL = "https://geocode-maps.yandex.ru/1.x/"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class WeatherStates(StatesGroup):
    start_city = State()
    end_city = State()
    intermediate_cities = State()
    days = State()

# Функции для получения данных о погоде и координатах
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
            return None  # Возвращаем None, если город не найден
        
        coordinates = geo_object.get("Point", {}).get("pos", "")
        if not coordinates:
            return None  # Возвращаем None, если координаты не найдены
        
        lon, lat = map(float, coordinates.split(" "))
        return lat, lon
    except requests.RequestException as e:
        raise ValueError(f"Ошибка подключения к Яндекс API: {str(e)}")
    except Exception as e:
        raise ValueError(f"Ошибка при обработке города '{city_name}': {str(e)}")

def get_weather_data(latitude, longitude, days=1):
    try:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max",
            "timezone": "auto",
            "forecast_days": days,
        }
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
    except requests.RequestException as e:
        raise Exception(f"Ошибка подключения к Open Meteo API: {e}")
    
    data = response.json()
    if not data:
        raise Exception("Данные API недоступны или некорректны.")
    
    return data

def parse_weather_data(raw_data):
    daily_data = raw_data.get("daily", {})
    days = len(daily_data.get("temperature_2m_max", []))

    forecast = []
    for i in range(days):
        forecast.append({
            "date": daily_data.get("time", [])[i],
            "max_temperature": daily_data.get("temperature_2m_max", [None])[i],
            "min_temperature": daily_data.get("temperature_2m_min", [None])[i],
            "precipitation_sum": daily_data.get("precipitation_sum", [None])[i],
            "wind_speed_max": daily_data.get("windspeed_10m_max", [None])[i],
        })
    return forecast

# Создание inline кнопок
def create_days_buttons():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(types.InlineKeyboardButton(text="1 день", callback_data="1"))
    keyboard.add(types.InlineKeyboardButton(text="3 дня", callback_data="3"))
    keyboard.add(types.InlineKeyboardButton(text="5 дней", callback_data="5"))
    keyboard.add(types.InlineKeyboardButton(text="7 дней", callback_data="7"))
    return keyboard.as_markup()

# Обработчик команды start
@dp.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    await message.answer("Привет! Введите /weather, чтобы узнать прогноз погоды.", reply_markup=create_start_button())

# Обработчик команды weather
@dp.message(Command("weather"))
async def weather_command(message: types.Message, state: FSMContext):
    await message.answer("Введите начальный город:")
    await state.set_state(WeatherStates.start_city)

# Обработчик для выбора количества дней
@dp.callback_query(lambda c: c.data.startswith("start"))
async def process_start_button(callback_query: types.CallbackQuery, state: FSMContext):
    # Начать новый диалог
    await callback_query.answer("Запрос на прогноз погоды начат.")
    await state.set_state(WeatherStates.start_city)
    await bot.send_message(callback_query.from_user.id, "Введите начальный город:")

@dp.callback_query(lambda c: c.data in ["1", "3", "5", "7"])
async def process_days_selection(callback_query: types.CallbackQuery, state: FSMContext):
    days = int(callback_query.data)
    await state.update_data(days=days)
    await callback_query.answer(f"Вы выбрали {days} дня(ей) прогноза.")
    await bot.send_message(callback_query.from_user.id, "Введите конечный город:")
    await state.set_state(WeatherStates.end_city)

# Обработчик начального города
@dp.message(WeatherStates.start_city)
async def process_start_city(message: types.Message, state: FSMContext):
    city_name = message.text.strip().lower()
    coordinates = get_coordinates(city_name)
    
    if coordinates is None:
        await message.answer(f"Город '{city_name.capitalize()}' не найден. Пожалуйста, попробуйте снова:")
        return

    await state.update_data(start_city=city_name)
    await message.answer("Выберите, на сколько дней вы хотите получить прогноз погоды:", reply_markup=create_days_buttons())
    await state.set_state(WeatherStates.days)

# Обработчик конечного города
@dp.message(WeatherStates.end_city)
async def process_end_city(message: types.Message, state: FSMContext):
    data = await state.get_data()
    start_city = data["start_city"]
    end_city = message.text.strip().lower()

    if start_city == end_city:
        await message.answer("Ошибка: начальный и конечный города не должны совпадать! Введите другой конечный город:")
        return
    
    coordinates = get_coordinates(end_city)
    if coordinates is None:
        await message.answer(f"Город '{end_city.capitalize()}' не найден. Пожалуйста, попробуйте снова:")
        return

    await state.update_data(end_city=end_city)
    await message.answer(
        "Введите промежуточные города через запятую (если их нет, напишите 'нет'):"
    )
    await state.set_state(WeatherStates.intermediate_cities)

# Обработчик промежуточных городов
@dp.message(WeatherStates.intermediate_cities)
async def process_intermediate_cities(message: types.Message, state: FSMContext):
    data = await state.get_data()
    start_city = data["start_city"]
    end_city = data["end_city"]
    intermediate_cities_input = message.text.strip().lower()

    if intermediate_cities_input == "нет":
        intermediate_cities = []
    else:
        intermediate_cities = [city.strip() for city in intermediate_cities_input.split(",") if city.strip()]

    if any(city in [start_city, end_city] for city in intermediate_cities):
        await message.answer("Ошибка: промежуточные города не должны совпадать с начальным или конечным городом. Попробуйте еще раз:")
        return

    route = f"{start_city.capitalize()} -> "
    if intermediate_cities:
        route += " -> ".join([city.capitalize() for city in intermediate_cities]) + " -> "
    route += f"{end_city.capitalize()}"

    # Получаем количество дней из состояния
    days = data.get('days', 1)

    # Получаем координаты и прогноз погоды для каждого города
    try:
        cities = [start_city] + intermediate_cities + [end_city]
        weather_report = ""
        for city in cities:
            try:
                lat, lon = get_coordinates(city)
            except ValueError as e:
                await message.answer(
                    f"Не удалось найти город '{city.capitalize()}'. "
                    "Пожалуйста, проверьте правильность ввода и попробуйте снова."
                )
                return

            weather_data = get_weather_data(lat, lon, days=days)
            forecast = parse_weather_data(weather_data)

            weather_report += f"Погода для города {city.capitalize()}:\n"
            for day in forecast:
                weather_report += (
                    f"Дата: {day['date']}\n"
                    f"Макс. температура: {day['max_temperature']}°C\n"
                    f"Мин. температура: {day['min_temperature']}°C\n"
                    f"Осадки: {day['precipitation_sum']} мм\n"
                    f"Макс. скорость ветра: {day['wind_speed_max']} м/с\n\n"
                )

        await message.answer(f"Ваш маршрут: {route}\n\n{weather_report}")
    except Exception as e:
        await message.answer(f"Ошибка при получении прогноза погоды: {str(e)}")

    await state.clear()


    # Получаем количество дней из состояния
    days = data.get('days', 1)

    # Получаем координаты и прогноз погоды для каждого города
    try:
        cities = [start_city] + intermediate_cities + [end_city]
        weather_report = ""
        for city in cities:
            lat, lon = get_coordinates(city)
            if lat is None or lon is None:
                await message.answer(f"Город '{city.capitalize()}' не найден. Пропускаем его.")
                continue
            weather_data = get_weather_data(lat, lon, days=days)
            forecast = parse_weather_data(weather_data)

            weather_report += f"Погода для города {city.capitalize()}:\n"
            for day in forecast:
                weather_report += (
                    f"Дата: {day['date']}\n"
                    f"Макс. температура: {day['max_temperature']}°C\n"
                    f"Мин. температура: {day['min_temperature']}°C\n"
                    f"Осадки: {day['precipitation_sum']} мм\n"
                    f"Макс. скорость ветра: {day['wind_speed_max']} м/с\n\n"
                )

        await message.answer(f"Ваш маршрут: {route}\n\n{weather_report}")
    except Exception as e:
        await message.answer(f"Ошибка при получении прогноза погоды: {str(e)}")

    await state.clear()

# Запуск бота
if __name__ == "__main__":
    async def main():
        await dp.start_polling(bot)

    asyncio.run(main())
