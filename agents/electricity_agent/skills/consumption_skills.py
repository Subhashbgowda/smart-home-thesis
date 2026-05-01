import os
import pandas as pd
from datetime import datetime, timedelta
import json

class ElectricitySkill:
    def __init__(self, csv_file="smart_home_clean_minute.csv", log_file="electricity_log.csv", state_file="electricity_state.json"):
        # Project root = folder outside 'agents'
        ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.csv_file = os.path.join(ROOT_DIR,"..", "data", csv_file)
        self.log_file = os.path.join(ROOT_DIR,"..", log_file)
        self.state_file = os.path.join(ROOT_DIR,"..", state_file)

        # Load CSV
        if not os.path.exists(self.csv_file):
            raise FileNotFoundError(f"CSV file not found at {self.csv_file}")
        self.df = pd.read_csv(self.csv_file, parse_dates=["time"])
        print(f"  Loaded CSV from: {self.csv_file}")

        # Load state if exists
        if os.path.exists(self.state_file):
            with open(self.state_file, "r") as f:
                state = json.load(f)
                self.current_index = state["last_index"]
                self.base_time = datetime.fromisoformat(state["base_time"])
        else:
            self.current_index = 0
            self.base_time = datetime.now()  # start now

        # Calculate original start time
        self.original_start_time = self.df["time"].iloc[0]

        # Create log file if missing
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                f.write("timestamp,house_overall_kw,dishwasher_kw,fridge_kw,microwave_kw,livingroom_kw\n")

    def get_current_consumption(self):
        """Return consumption at current step, shift timestamp to live time, and log it."""
        if self.current_index >= len(self.df):
            print("⚠️ Reached end of CSV dataset.")
            return None

        row = self.df.iloc[self.current_index]

        # Calculate time difference from original start
        delta = row["time"] - self.original_start_time
        live_time = self.base_time + delta

        consumption = {
            "timestamp": live_time,
            "house_overall_kw": row["house_overall_kw"],
            "dishwasher_kw": row["dishwasher_kw"],
            "fridge_kw": row["fridge_kw"],
            "microwave_kw": row["microwave_kw"],
            "livingroom_kw": row["livingroom_kw"]
        }

        # Log to CSV
        with open(self.log_file, "a") as f:
            f.write(f"{consumption['timestamp']},{consumption['house_overall_kw']},"
                    f"{consumption['dishwasher_kw']},{consumption['fridge_kw']},"
                    f"{consumption['microwave_kw']},{consumption['livingroom_kw']}\n")

        # Update state
        self.current_index += 1
        self._save_state()

        return consumption

    def _save_state(self):
        state = {
            "last_index": self.current_index,
            "base_time": self.base_time.isoformat()
        }
        with open(self.state_file, "w") as f:
            json.dump(state, f)
