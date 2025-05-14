import requests
from datetime import datetime, timedelta
from config import WEATHER_API_KEY

def get_weather(day_offset=0):
    try:
        base_url = "https://api.weatherapi.com/v1/forecast.json"
        params = {
            "key": WEATHER_API_KEY,
            "q": "Chicago",
            "days": day_offset + 1,
            "aqi": "no",
            "alerts": "no"
        }

        response = requests.get(base_url, params=params)
        data = response.json()

        forecast_day = data["forecast"]["forecastday"][day_offset]
        date_str = forecast_day["date"]
        condition = forecast_day["day"]["condition"]["text"].lower()
        temp = forecast_day["day"]["maxtemp_f"]

        if day_offset == 0:
            label = "Today"
        elif day_offset == 1:
            label = "Tomorrow"
        else:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            label = f"On {date_obj.strftime('%A')}"

        return f"{label} in Chicago, expect {condition} with a high of {temp}°F."

    except Exception as e:
        return f"Couldn’t get weather. Error: {e}"
    
def get_weather_summary():
    try:
        base_url = "https://api.weatherapi.com/v1/forecast.json"
        params = {
            "key": WEATHER_API_KEY,
            "q": "Chicago",
            "days": 5,
            "aqi": "no",
            "alerts": "no"
        }

        response = requests.get(base_url, params=params)
        data = response.json()

        summary_lines = []

        for i, day in enumerate(data["forecast"]["forecastday"]):
            date_obj = datetime.strptime(day["date"], "%Y-%m-%d")
            weekday = date_obj.strftime("%A")
            desc = day["day"]["condition"]["text"].lower()
            rain_chance = day["day"].get("daily_chance_of_rain", 0)

            if i == 0:
                label = "Today"
            elif i == 1:
                label = "Tomorrow"
            else:
                label = f"On {weekday}"

            if rain_chance >= 50:
                line = f"{label}, expect {desc} with a {rain_chance}% chance of rain."
            elif rain_chance > 0:
                line = f"{label}, it should be {desc} with only a {rain_chance}% chance of rain."
            else:
                line = f"{label}, it’ll be {desc} and dry all day."

            summary_lines.append(line)

        return "Here’s the 5-day forecast for Chicago:\n" + "\n".join(summary_lines)

    except Exception as e:
        return f"Couldn’t get weather summary. Error: {e}"
    
def get_weekend_weather_summary():
    try:
        base_url = "https://api.weatherapi.com/v1/forecast.json"
        params = {
            "key": WEATHER_API_KEY,
            "q": "Chicago",
            "days": 5,
            "aqi": "no",
            "alerts": "no"
        }

        response = requests.get(base_url, params=params)
        data = response.json()

        summary_lines = []
        weekend_days = ["Saturday", "Sunday"]

        for day in data["forecast"]["forecastday"]:
            date_obj = datetime.strptime(day["date"], "%Y-%m-%d")
            weekday = date_obj.strftime("%A")

            if weekday not in weekend_days:
                continue

            desc = day["day"]["condition"]["text"].lower()
            rain_chance = day["day"].get("daily_chance_of_rain", 0)

            label = f"On {weekday}"

            if rain_chance >= 50:
                line = f"{label}, expect {desc} with a {rain_chance}% chance of rain."
            elif rain_chance > 0:
                line = f"{label}, it should be {desc} with only a {rain_chance}% chance of rain."
            else:
                line = f"{label}, it’ll be {desc} and dry all day."

            summary_lines.append(line)

        return "Here’s the weekend forecast for Chicago:\n" + "\n".join(summary_lines)

    except Exception as e:
        return f"Couldn’t get weekend weather. Error: {e}"