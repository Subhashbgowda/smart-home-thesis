# agents/ml_main_control_agent/ml_main_control_agent.py

import os
import json
import time
import datetime
import argparse
from dotenv import load_dotenv
load_dotenv()

from agents.pricing_agent.skills.pricing_skill import PricingSkill
from agents.weather_agent.skills.weather_skill import WeatherSkill
from agents.electricity_agent.skills.consumption_skills import ElectricitySkill
from agents.occupancy_agent.skills.occupancy_skill import OccupancySkill
from agents.ml_main_control_agent.skills.ml_main_control_skill import MLMainControlSkill


# ================================================================
# PROJECT PATHS
# ================================================================
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

INTERVAL_FILE = os.path.join(PROJECT_ROOT, "log_interval.txt")
ML_LOG_FILE = os.path.join(PROJECT_ROOT, "ml_control_log.csv")


# ================================================================
# Read logging interval written by backend
# ================================================================
def get_interval():
    """Reads the dynamic interval (in seconds) set by the backend."""
    try:
        if os.path.exists(INTERVAL_FILE):
            with open(INTERVAL_FILE, "r") as f:
                val = int(float(f.read().strip()))
                return max(1, val)
    except:
        pass
    return 1  # default fallback


# ================================================================
# MAIN AGENT LOOP
# ================================================================
def main(simulate=0, verbose=False):

    # --- Pricing API URL ---
    today = datetime.date.today()
    start = today.strftime("%Y-%m-%dT00:00:00Z")
    end   = today.strftime("%Y-%m-%dT23:59:59Z")
    api_url = f"https://dashboard.elering.ee/api/nps/price?start={start}&end={end}"

    # --- Initialize Skills ---
    pricing_skill = PricingSkill(api_url=api_url, country="ee")
    weather_skill = WeatherSkill(api_key=os.getenv("OPENWEATHER_API_KEY"),
                                 city="Kosice", country="SK")

    csv_data_path = os.path.join(PROJECT_ROOT, "data", "smart_home_clean_minute.csv")

    electricity_skill = ElectricitySkill(csv_file=csv_data_path)
    occupancy_skill   = OccupancySkill(csv_file=csv_data_path)

    # --- Initialize ML Control Skill ---
    control_skill = MLMainControlSkill(
        pricing_skill,
        weather_skill,
        electricity_skill,
        occupancy_skill,
        csv_log_path=ML_LOG_FILE,   # always write to ml_control_log.csv
    )

    # ================================================================
    # SIMULATION MODE
    # ================================================================
    if simulate > 0:
        for _ in range(simulate):
            try:
                control_skill.run_cycle(verbose=verbose)
            except Exception as e:
                print("Simulation cycle error:", e)
            time.sleep(0.1)
        return

    # ================================================================
    # REALTIME MODE — RUN FOREVER UNTIL STOPPED
    # ================================================================
    print("ML Control Agent is running in realtime mode...")

    try:
        while True:
            try:
                control_skill.run_cycle(verbose=verbose)
            except Exception as e:
                print("Runtime cycle error:", e)

            # dynamic interval from backend
            time.sleep(get_interval())

    except KeyboardInterrupt:
        print("Stopping ML Control Agent...")


# ================================================================
# SCRIPT ENTRY POINT
# ================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--simulate", type=int, default=0)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    main(simulate=args.simulate, verbose=args.verbose)
