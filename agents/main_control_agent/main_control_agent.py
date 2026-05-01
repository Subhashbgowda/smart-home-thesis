# agents/main_control_agent/main_control_agent.py
import json
import datetime
import time
import os
import argparse
from dotenv import load_dotenv
load_dotenv()

from agents.pricing_agent.skills.pricing_skill import PricingSkill
from agents.weather_agent.skills.weather_skill import WeatherSkill
from agents.electricity_agent.skills.consumption_skills import ElectricitySkill
from agents.occupancy_agent.skills.occupancy_skill import OccupancySkill
from agents.main_control_agent.skills.main_control_skill import MainControlSkill

def main(simulate=0, verbose=False):
    # pricing api url for today (used only by run_cycle; simulate bypasses it)
    today = datetime.date.today()
    start = today.strftime("%Y-%m-%dT00:00:00Z")
    end   = today.strftime("%Y-%m-%dT23:59:59Z")
    api_url = f"https://dashboard.elering.ee/api/nps/price?start={start}&end={end}"

    pricing_skill = PricingSkill(api_url=api_url, country="ee")
    # weather skill expects API key in .env: OPENWEATHER_API_KEY
    weather_skill = WeatherSkill(api_key=os.getenv("OPENWEATHER_API_KEY"), city="Kosice", country="SK")

    csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "smart_home_clean_minute.csv"))
    electricity_skill = ElectricitySkill(csv_file=csv_path)
    occupancy_skill = OccupancySkill(csv_file="smart_home_clean_minute.csv")  # path inside OccupancySkill resolves to data dir

    control_skill = MainControlSkill(pricing_skill, weather_skill, electricity_skill, occupancy_skill)

    if simulate and simulate > 0:
        control_skill.simulate_data(cycles=simulate, verbose=verbose)
        return

    # otherwise run realtime loop
    try:
        while True:
            row = control_skill.run_cycle(verbose=verbose)
            print(json.dumps(row, indent=2))
            time.sleep(1)  # production interval (change to 1 for faster dev)
    except KeyboardInterrupt:
        print("Stopping...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--simulate", type=int, default=0, help="Number of synthetic cycles to generate.")
    parser.add_argument("--verbose", action="store_true", help="Print progress while running.")
    args = parser.parse_args()
    main(simulate=args.simulate, verbose=args.verbose)
