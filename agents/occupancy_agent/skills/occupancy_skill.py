# agents/occupancy_agent/skills/occupancy_skill.py
import os
import pandas as pd
import datetime
import json

class OccupancySkill:
    def __init__(self, csv_file="smart_home_clean_minute.csv", log_file="occupancy_log.csv", state_file="occupancy_state.json", threshold=1.0):
        ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.csv_file = os.path.abspath(os.path.join(ROOT_DIR, "..", "data", csv_file))
        self.log_file = os.path.abspath(os.path.join(ROOT_DIR, "..", log_file))
        self.state_file = os.path.abspath(os.path.join(ROOT_DIR, "..", state_file))
        self.threshold = threshold

        if not os.path.exists(self.csv_file):
            raise FileNotFoundError(f"CSV file not found at {self.csv_file}")
        self.df = pd.read_csv(self.csv_file, parse_dates=["time"])
        print(f"  Loaded occupancy CSV from: {self.csv_file}")

        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                f.write("timestamp,occupied,house_overall_kw\n")

        self.current_index = self._load_state()

    def _load_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, "r") as f:
                state = json.load(f)
                return state.get("last_index", 0)
        return 0

    def _save_state(self):
        with open(self.state_file, "w") as f:
            json.dump({"last_index": self.current_index}, f)

    def get_next_status(self):
        if self.current_index >= len(self.df):
            self.current_index = 0
        row = self.df.iloc[self.current_index]
        self.current_index += 1
        self._save_state()

        occupied = bool(row["house_overall_kw"] > self.threshold)
        status = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "occupied": occupied,
            "house_overall_kw": float(row["house_overall_kw"])
        }
        with open(self.log_file, "a") as f:
            f.write(f"{status['timestamp']},{status['occupied']},{status['house_overall_kw']}\n")
        return status

    # wrapper expected by MainControlSkill
    def get_current_occupancy(self):
        return self.get_next_status()
