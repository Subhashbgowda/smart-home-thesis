import requests
import json
import datetime
import os
import csv

class WeatherSkill:
    def __init__(self, api_key, latitude=None, longitude=None, city=None, country=None, log_file="weather_log.csv"):
        self.api_key = api_key
        self.latitude = latitude
        self.longitude = longitude
        self.city = city
        self.country = country
        self.log_file = log_file

        if not os.path.exists(self.log_file):
            with open(self.log_file, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["timestamp", "temperature", "humidity", "condition"])

    def fetch_weather(self):
        if self.latitude and self.longitude:
            url = f"http://api.openweathermap.org/data/2.5/weather?lat={self.latitude}&lon={self.longitude}&appid={self.api_key}&units=metric"
        elif self.city and self.country:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={self.city},{self.country}&appid={self.api_key}&units=metric"
        else:
            return {"error": "No location provided"}

        response = requests.get(url)
        data = response.json()

        if response.status_code != 200:
            return {"error": data.get("message", "Failed to fetch weather")}

        weather_info = {
            "timestamp": datetime.datetime.now().isoformat(),
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "condition": data["weather"][0]["main"]
        }

        with open(self.log_file, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(weather_info.values())

        return weather_info
