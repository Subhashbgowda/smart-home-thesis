import os
import json
from dotenv import load_dotenv
from agents.weather_agent.skills.weather_skill import WeatherSkill

# Load environment variables
load_dotenv()

def main():
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        raise ValueError("❌ Missing OPENWEATHER_API_KEY in .env file")

    # Initialize skill
    weather_skill = WeatherSkill(api_key=api_key, city="Kosice", country="SK")

    # Fetch weather once
    result = weather_skill.fetch_weather()
    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    main()
