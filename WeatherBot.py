import asyncio
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters.command import Command

# Telegram bot token
BOT_TOKEN = "7767062312:AAEU4KR9Mk8NlwMH6vcsQ92m6fDkKOSkMtk"

# URL для Яндекс.Погоды
YANDEX_WEATHER_URL = "https://yandex.ru/pogoda/moscow"

# Создаем экземпляры бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Функция для парсинга прогноза погоды
def parse_weather():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(YANDEX_WEATHER_URL, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    weather_data = []

    # Извлечение данных о погоде
    today = datetime.now().strftime("%Y-%m-%d")
    days = soup.select(".forecast-briefly__day")
    for day in days:
        date_elem = day.select_one("time")
        if date_elem and date_elem["datetime"] >= today:
            date = day.select_one(".forecast-briefly__name").text
            day_temp = day.select_one(".temp__value").text
            night_temp = day.select(".temp__value")[1].text if len(day.select(".temp__value")) > 1 else "N/A"
            weather_data.append(f"{date}: днём {day_temp}°C, ночью {night_temp}°C")
            if len(weather_data) == 7:
                break
    return "\n".join(weather_data)

# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer("Привет! Напиши /weather, чтобы узнать прогноз на 7 дней по Москве.")

# Обработчик команды /weather
@dp.message(Command("weather"))
async def send_weather(message: Message):
    try:
        weather_report = parse_weather()
        await message.answer(f"Прогноз погоды на 7 дней по Москве:\n\n{weather_report}")
    except Exception as e:
        await message.answer(f"Ошибка при получении прогноза погоды: {e}")

# Основной блок запуска
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
