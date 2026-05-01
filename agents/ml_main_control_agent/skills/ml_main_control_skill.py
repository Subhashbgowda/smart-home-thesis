import os
import joblib
import csv
from datetime import datetime
import pytz
from dateutil import parser


class MLMainControlSkill:
    """
    ML-based control using quantile-based electricity price levels.
    """

    def __init__(
        self,
        pricing_skill,
        weather_skill,
        electricity_skill,
        occupancy_skill,
        csv_log_path="ml_control_log.csv",
        project_root=None,
    ):
        self.pricing_skill = pricing_skill
        self.weather_skill = weather_skill
        self.electricity_skill = electricity_skill
        self.occupancy_skill = occupancy_skill

        self.project_root = project_root or os.getcwd()
        self.csv_log_path = (
            csv_log_path if os.path.isabs(csv_log_path)
            else os.path.join(self.project_root, csv_log_path)
        )

        self.model = joblib.load(
            os.path.join(self.project_root, "models", "trained_policy.pkl")
        )
        self.encoder = joblib.load(
            os.path.join(self.project_root, "models", "encoder.pkl")
        )

        self.condition_categories = self.encoder.categories_[0]
        self.price_categories = self.encoder.categories_[1]

    # --------------------------------------------------
    # COMFORT MODE
    # --------------------------------------------------
    def _read_comfort_mode(self):
        try:
            path = os.path.join(self.project_root, "comfort_mode.txt")
            if os.path.exists(path):
                raw = open(path).read().strip().lower()
                return raw in ("1", "true", "yes", "on")
        except Exception:
            pass
        return False

    # --------------------------------------------------
    # PRICE LEVEL (QUANTILE-BASED)
    # --------------------------------------------------
    def _compute_price_level(self, prices, current_price):
        try:
            if not prices or current_price is None:
                return "low"

            values = [
                float(p["price_eur_per_kwh"])
                for p in prices
                if isinstance(p, dict) and "price_eur_per_kwh" in p
            ]

            if len(values) < 3:
                return "low"

            values.sort()
            low_q = values[int(0.3 * len(values))]
            high_q = values[int(0.7 * len(values))]

            if current_price <= low_q:
                return "low"
            elif current_price >= high_q:
                return "high"
            else:
                return "medium"

        except Exception:
            return "low"

    # --------------------------------------------------
    # MAIN CYCLE
    # --------------------------------------------------
    def run_cycle(self, simulated_time=None, verbose=False):

        prices = self.pricing_skill.fetch_electricity_prices()
        weather = self.weather_skill.fetch_weather()
        electricity = self.electricity_skill.get_current_consumption()
        occupancy = self.occupancy_skill.get_current_occupancy()

        row, features = self._prepare_features(
            prices, weather, electricity, occupancy, simulated_time
        )

        comfort = self._read_comfort_mode()
        row["comfort_mode"] = int(comfort)

        if comfort:
            row["action"] = "Comfort mode ON — keep all appliances running"
            row["confidence"] = 1.0
            self._append_to_csv(row)
            return row

        if occupancy.get("occupied") is False:
            row["action"] = "Turn off lights"
            row["confidence"] = 1.0
            self._append_to_csv(row)
            return row

        try:
            pred = self.model.predict([features])[0]
            conf = max(self.model.predict_proba([features])[0])
        except Exception:
            pred, conf = "Normal operation", 0.5

        row["action"] = pred
        row["confidence"] = conf

        if verbose:
            print(row)

        self._append_to_csv(row)
        return row

    # --------------------------------------------------
    # FEATURE PREPARATION
    # --------------------------------------------------
    def _prepare_features(self, prices, weather, electricity, occupancy, simulated_time=None):

        tz = pytz.timezone("Europe/Bratislava")

        # -------- USE SIMULATED TIME IF PROVIDED --------
        if simulated_time is not None:
            ts = simulated_time.astimezone(tz)
        else:
            ts = datetime.now(tz)

        # --- PRICE NOW ---
        try:
            def parse_time(t):
                dt = parser.isoparse(t)
                return dt if dt.tzinfo else tz.localize(dt)

            closest = min(prices, key=lambda x: abs(parse_time(x["time"]) - ts))
            price_value = float(closest["price_eur_per_kwh"])
        except Exception:
            price_value = 0.0

        price_level = self._compute_price_level(prices, price_value)

        # --- WEATHER ---
        temperature = weather.get("temperature", 0.0)
        humidity = weather.get("humidity", 0)
        condition = weather.get("condition", "Clear")

        # --- ELECTRICITY ---
        house_kw = electricity.get("house_overall_kw", 0.0)
        dishwasher_kw = electricity.get("dishwasher_kw", 0.0)
        fridge_kw = electricity.get("fridge_kw", 0.0)
        microwave_kw = electricity.get("microwave_kw", 0.0)
        livingroom_kw = electricity.get("livingroom_kw", 0.0)

        occupied = occupancy.get("occupied", 0)

        hour = ts.hour
        dow = ts.weekday()
        is_weekend = 1 if dow >= 5 else 0
        budget_remaining = 100.0

        # --- ONE-HOT ---
        X_cat = {}
        for c in self.condition_categories:
            X_cat[f"condition_{c}"] = 1 if condition == c else 0

        for p in self.price_categories:
            X_cat[f"price_level_{p}"] = 1 if price_level == p else 0

        X_num = [
            price_value,
            temperature,
            humidity,
            house_kw,
            dishwasher_kw,
            fridge_kw,
            microwave_kw,
            livingroom_kw,
            occupied,
            hour,
            dow,
            is_weekend,
            budget_remaining,
        ]

        row = {
            "timestamp": ts.isoformat(),
            "price_eur_per_kwh": price_value,
            "temperature": temperature,
            "humidity": humidity,
            "house_overall_kw": house_kw,
            "dishwasher_kw": dishwasher_kw,
            "fridge_kw": fridge_kw,
            "microwave_kw": microwave_kw,
            "livingroom_kw": livingroom_kw,
            "occupied": occupied,
            "hour_of_day": hour,
            "day_of_week": dow,
            "is_weekend": is_weekend,
            "budget_remaining": budget_remaining,
            "price_level": price_level,
            "condition": condition,
            **X_cat,
        }

        features = X_num + list(X_cat.values())

        return row, features

    # --------------------------------------------------
    # CSV LOGGING
    # --------------------------------------------------
    def _append_to_csv(self, row):
        exists = os.path.isfile(self.csv_log_path)
        with open(self.csv_log_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            if not exists:
                writer.writeheader()
            writer.writerow(row)
