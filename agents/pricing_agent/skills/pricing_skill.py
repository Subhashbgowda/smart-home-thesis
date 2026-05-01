import requests
import json
import datetime
import os
import csv


class PricingSkill:
    def __init__(self, api_url, country="ee", log_file="pricing_log.csv"):
        self.api_url = api_url
        self.country = country  # 'ee', 'fi', 'lv', or 'lt'
        self.log_file = log_file

        # Create CSV with headers if it does not exist
        if not os.path.exists(self.log_file):
            with open(self.log_file, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["time", "price_eur_per_kwh"])

    def fetch_electricity_prices(self):
        response = requests.get(self.api_url)

        if response.status_code != 200:
            return {"error": f"API request failed with {response.status_code}"}

        data = response.json()
        prices = []

        if data.get("success") and "data" in data and self.country in data["data"]:
            with open(self.log_file, mode="a", newline="") as file:
                writer = csv.writer(file)

                for entry in data["data"][self.country]:
                    # Convert Unix timestamp → human-readable time
                    dt = datetime.datetime.utcfromtimestamp(entry["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
                    # Convert price from EUR/MWh → EUR/kWh
                    price_kwh = entry["price"] / 1000
                    prices.append({"time": dt, "price_eur_per_kwh": round(price_kwh, 4)})

                    # Log into CSV
                    writer.writerow([dt, round(price_kwh, 4)])

        return prices

    def generate_report(self):
        prices = self.fetch_electricity_prices()
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "electricity_prices": prices
        }
        return json.dumps(report, indent=4)
