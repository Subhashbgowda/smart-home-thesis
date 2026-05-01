import datetime
import os
import csv
import random


class MainControlSkill:
    """
    Rule-based main decision-making skill.
    Uses relative electricity price levels based on daily quantiles.
    """

    def __init__(self, pricing_skill, weather_skill, electricity_skill, occupancy_skill, log_file=None):
        self.pricing_skill = pricing_skill
        self.weather_skill = weather_skill
        self.electricity_skill = electricity_skill
        self.occupancy_skill = occupancy_skill

        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        self.project_root = project_root
        self.log_file = log_file or os.path.join(project_root, "control_log.csv")
        self.comfort_file = os.path.join(project_root, "comfort_mode.txt")

        self._ensure_csv()

    # --------------------------------------------------
    # CSV SETUP
    # --------------------------------------------------
    def _ensure_csv(self):
        headers = [
            "timestamp",
            "price_eur_per_kwh",
            "temperature",
            "humidity",
            "condition",
            "house_overall_kw",
            "dishwasher_kw",
            "fridge_kw",
            "microwave_kw",
            "livingroom_kw",
            "occupied",
            "hour_of_day",
            "day_of_week",
            "is_weekend",
            "price_level",
            "comfort_mode",
            "action",
        ]

        if not os.path.exists(self.log_file):
            with open(self.log_file, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(headers)

    def _read_comfort(self):
        try:
            if os.path.exists(self.comfort_file):
                raw = open(self.comfort_file).read().strip().lower()
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
    # SENSOR NOISE
    # --------------------------------------------------
    def _add_sensor_noise(self, electricity):
        if not electricity:
            return {}

        out = dict(electricity)
        for k in [
            "house_overall_kw",
            "dishwasher_kw",
            "fridge_kw",
            "microwave_kw",
            "livingroom_kw",
        ]:
            try:
                out[k] = round(float(out.get(k, 0)) * random.uniform(0.95, 1.05), 6)
            except Exception:
                pass
        return out

    # --------------------------------------------------
    # MAIN CYCLE
    # --------------------------------------------------
    def run_cycle(self, simulated_time=None, verbose=False):

        prices = self.pricing_skill.fetch_electricity_prices()

        # -------- USE SIMULATED TIME IF PROVIDED --------
        if simulated_time is not None:
            now_utc = simulated_time.astimezone(datetime.timezone.utc).replace(
                minute=0, second=0, microsecond=0
            )
            ts = simulated_time.astimezone(datetime.timezone.utc).replace(
                microsecond=0
            )
        else:
            now_utc = datetime.datetime.now(datetime.timezone.utc).replace(
                minute=0, second=0, microsecond=0
            )
            ts = datetime.datetime.now(datetime.timezone.utc).replace(
                microsecond=0
            )

        # --- PRICE NOW ---
        price_now = None

        try:
            closest = min(
                prices,
                key=lambda x: abs(
                    datetime.datetime.fromisoformat(x["time"]).astimezone(datetime.timezone.utc)
                    - now_utc
                ),
            )
            price_now = float(closest["price_eur_per_kwh"])
        except Exception:
            price_now = 0.0

        # --- OTHER INPUTS ---
        weather = self.weather_skill.fetch_weather() or {}
        electricity = self._add_sensor_noise(
            self.electricity_skill.get_current_consumption() or {}
        )
        occupancy = self.occupancy_skill.get_current_occupancy() or {}

        # --- TIME FEATURES ---
        hour = ts.hour
        dow = ts.weekday()
        is_weekend = 1 if dow >= 5 else 0

        price_level = self._compute_price_level(prices, price_now)
        comfort = self._read_comfort()

        # --- DECISION ---
        if comfort:
            action = "Comfort mode active: keep all appliances ON"
        else:
            action = self.decide_action(price_now, weather, electricity, occupancy.get("occupied"))

        row = {
            "timestamp": ts.isoformat(),
            "price_eur_per_kwh": price_now,
            "temperature": weather.get("temperature"),
            "humidity": weather.get("humidity"),
            "condition": weather.get("condition"),
            "house_overall_kw": electricity.get("house_overall_kw"),
            "dishwasher_kw": electricity.get("dishwasher_kw"),
            "fridge_kw": electricity.get("fridge_kw"),
            "microwave_kw": electricity.get("microwave_kw"),
            "livingroom_kw": electricity.get("livingroom_kw"),
            "occupied": occupancy.get("occupied"),
            "hour_of_day": hour,
            "day_of_week": dow,
            "is_weekend": is_weekend,
            "price_level": price_level,
            "comfort_mode": int(comfort),
            "action": action,
        }

        self.log_decision(row)

        if verbose:
            print(row)

        return row

    # --------------------------------------------------
    # RULE LOGIC
    # --------------------------------------------------
    def decide_action(self, price, weather, electricity, occupied):
        if occupied is False:
            return "Turn off non-essential devices (unoccupied)"
        if electricity.get("house_overall_kw", 0) > 2.5:
            return "Reduce appliance usage (high load)"
        if weather and str(weather.get("condition", "")).lower() in ["clear", "sunny"]:
            return "Good time to run appliances"
        return "Normal operation"

    # --------------------------------------------------
    # LOGGING
    # --------------------------------------------------
    def log_decision(self, row):
        with open(self.log_file, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(row.values())
