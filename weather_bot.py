import os
import requests

# --- Настройки ---
CITY = "Вишнёвое"
LAT, LON = 50.3883, 30.3714
TIMEZONE = "Europe/Kyiv"

BOT_TOKEN = os.environ["BOT_TOKEN"]   # токен от @BotFather
CHAT_ID = os.environ["CHAT_ID"]       # твой chat_id

WEATHER_CODES = {
    0: "ясно", 1: "преимущественно ясно", 2: "переменная облачность", 3: "пасмурно",
    45: "туман", 48: "изморозь", 51: "лёгкая морось", 53: "морось", 55: "сильная морось",
    56: "ледяная морось", 57: "сильная ледяная морось",
    61: "небольшой дождь", 63: "дождь", 65: "сильный дождь",
    66: "ледяной дождь", 67: "сильный ледяной дождь",
    71: "небольшой снег", 73: "снег", 75: "сильный снег", 77: "снежные зёрна",
    80: "небольшие ливни", 81: "ливни", 82: "сильные ливни",
    85: "снегопад", 86: "сильный снегопад",
    95: "гроза", 96: "гроза с градом", 99: "сильная гроза с градом",
}


def get_weather():
    r = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": LAT,
            "longitude": LON,
            "timezone": TIMEZONE,
            "current": "temperature_2m,apparent_temperature",
            "daily": ",".join([
                "weather_code", "temperature_2m_max", "temperature_2m_min",
                "precipitation_sum", "precipitation_probability_max", "wind_speed_10m_max",
            ]),
            "forecast_days": 1,
        },
        timeout=20,
    )
    r.raise_for_status()
    return r.json()


def build_message(data):
    cur, day = data["current"], data["daily"]
    desc = WEATHER_CODES.get(day["weather_code"][0], "без описания")
    rain_chance = day["precipitation_probability_max"][0]
    rain_mm = day["precipitation_sum"][0]

    lines = [
        f"Доброе утро! Погода сегодня, {CITY}:",
        f"{desc.capitalize()}",
        f"Сейчас: {cur['temperature_2m']:.0f}°C (ощущается как {cur['apparent_temperature']:.0f}°C)",
        f"Днём: от {day['temperature_2m_min'][0]:.0f}°C до {day['temperature_2m_max'][0]:.0f}°C",
        f"Осадки: {rain_mm:.1f} мм, вероятность до {rain_chance}%",
        f"Ветер: до {day['wind_speed_10m_max'][0]:.0f} км/ч",
    ]
    if rain_chance is not None and rain_chance >= 50:
        lines.append("Лучше взять зонт.")
    return "\n".join(lines)


def send_telegram(text):
    r = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": text},
        timeout=20,
    )
    r.raise_for_status()


if __name__ == "__main__":
    send_telegram(build_message(get_weather()))
