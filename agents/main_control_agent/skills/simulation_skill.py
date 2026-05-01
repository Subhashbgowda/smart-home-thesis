# agents/main_control_agent/skills/simulation_skill.py
import datetime
import random
import os
import csv

class SimulationSkill:
    """
    Generates a highly realistic synthetic smart-home dataset with:
    - Probabilistic appliance usage
    - Occupancy variability
    - Weather variations (including snow, rain, clear, sunny, clouds, thunderstorm)
    - Price fluctuations
    - Budget fluctuations
    - Probabilistic actions instead of deterministic rules
    """

    def __init__(self, log_file=None):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        self.log_file = log_file or os.path.join(project_root, "control_log.csv")

        # Create file with headers if not exists
        if not os.path.exists(self.log_file):
            with open(self.log_file, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([
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
                    "action",
                    "budget_remaining"
                ])

    def _add_sensor_noise(self, electricity):
        """Add random noise (±10%) to appliance readings"""
        for k in electricity:
            if electricity[k] is not None:
                electricity[k] = round(float(electricity[k]) * random.uniform(0.9, 1.1), 6)
        return electricity

    def decide_action(self, price, electricity, occupied, budget_remaining):
        """
        Probabilistic decision-making based on:
        - Occupancy
        - Price
        - Load
        - Budget
        """
        # Unoccupied: mostly turn off non-essential devices
        if not occupied:
            return random.choices(
                ["Turn off non-essential devices (unoccupied)", "Normal operation"],
                weights=[0.85, 0.15], k=1
            )[0]

        # High load: reduce appliance usage
        if electricity["house_overall_kw"] > 2.5:
            return random.choices(
                ["Reduce appliance usage (high load)", "Normal operation"],
                weights=[0.7, 0.3], k=1
            )[0]

        # High price or low budget: delay appliances
        if price > 0.25 or budget_remaining < 20:
            return random.choices(
                ["Delay appliance usage (high price / low budget)", "Normal operation"],
                weights=[0.8, 0.2], k=1
            )[0]

        # Low load and affordable: good time to run appliances
        if electricity["house_overall_kw"] < 0.7 and price < 0.15:
            return random.choices(
                ["Good time to run appliances (low load & affordable)", "Normal operation"],
                weights=[0.7, 0.3], k=1
            )[0]

        # Default normal operation
        return "Normal operation"

    def simulate_data(self, cycles=20000, verbose=True):
        """Generate dataset with realistic variations"""
        weather_conditions = ["Clear", "Sunny", "Clouds", "Rain", "Thunderstorm", "Snow"]
        start_time = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        start_time -= datetime.timedelta(days=start_time.weekday())  # start Monday

        budget = 100  # initial budget

        for i in range(cycles):
            minutes_per_cycle = (7 * 24 * 60) / cycles  # spread over 7 days
            fake_time = start_time + datetime.timedelta(minutes=i * minutes_per_cycle)
            hour = fake_time.hour
            weekday = fake_time.weekday()

            # Electricity price with fluctuations
            base_price = 0.1 if 0 <= hour < 7 else 0.2 if 7 <= hour <= 9 else 0.15 if 10 <= hour <= 16 else 0.25 if 17 <= hour <= 20 else 0.12
            price = round(base_price + random.uniform(-0.05, 0.05), 3)

            # Weather simulation
            condition = random.choices(
                weather_conditions,
                weights=[0.2, 0.15, 0.2, 0.15, 0.1, 0.2],  # slightly higher chance for snow if needed
                k=1
            )[0]

            # Temperature realistic for condition
            if condition == "Snow":
                temperature = round(random.uniform(-10, 0), 2)
            elif condition == "Rain":
                temperature = round(random.uniform(0, 15), 2)
            elif condition == "Sunny" or condition == "Clear":
                temperature = round(random.uniform(5, 35), 2)
            else:  # Clouds, Thunderstorm
                temperature = round(random.uniform(0, 25), 2)

            humidity = random.randint(30, 100)

            # Occupancy pattern
            if weekday < 5:  # weekdays
                if 9 <= hour <= 16:
                    occupied = random.random() < 0.2
                else:
                    occupied = random.random() < 0.85
            else:  # weekend
                occupied = random.random() < 0.9

            # occasional random presence/absence
            if random.random() < 0.03:
                occupied = not occupied

            # Electricity usage patterns
            base_load = random.uniform(0.1, 0.6) if not occupied else random.uniform(0.4, 1.5)
            # random spikes
            if random.random() < 0.1:
                base_load += random.uniform(0.5, 3.0)

            electricity = {
                "house_overall_kw": round(base_load, 6),
                "dishwasher_kw": round(random.uniform(0, 0.8) if occupied and random.random() < 0.05 else random.uniform(0, 0.02), 6),
                "fridge_kw": round(random.uniform(0.04, 0.12), 6),  # always some consumption
                "microwave_kw": round(random.uniform(0, 0.6) if occupied and random.random() < 0.03 else random.uniform(0, 0.02), 6),
                "livingroom_kw": round(random.uniform(0, 0.5) if occupied else random.uniform(0, 0.02), 6)
            }

            electricity = self._add_sensor_noise(electricity)

            # Budget dynamics: reduce based on consumption and price
            budget_remaining = max(0, budget - electricity["house_overall_kw"] * price)

            # Decide action probabilistically
            action = self.decide_action(price, electricity, occupied, budget_remaining)

            price_level = "high" if price > 0.2 else "low"

            row = [
                fake_time.isoformat(),
                price,
                temperature,
                humidity,
                condition,
                electricity["house_overall_kw"],
                electricity["dishwasher_kw"],
                electricity["fridge_kw"],
                electricity["microwave_kw"],
                electricity["livingroom_kw"],
                occupied,
                hour,
                weekday,
                1 if weekday >= 5 else 0,
                price_level,
                action,
                round(budget_remaining, 2)
            ]

            # Append to CSV
            with open(self.log_file, mode="a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(row)

            if verbose and i % 500 == 0:
                print(f"Simulated {i}/{cycles} rows... latest action={action}")

        print(f"  Simulation complete: {cycles} rows written to {self.log_file}")
