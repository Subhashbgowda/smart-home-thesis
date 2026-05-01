from agents.pricing_agent.skills.pricing_skill import PricingSkill
import datetime
import numpy as np

today = datetime.date.today()
start = today.strftime("%Y-%m-%dT00:00:00Z")
end   = today.strftime("%Y-%m-%dT23:59:59Z")

api_url = f"https://dashboard.elering.ee/api/nps/price?start={start}&end={end}"

ps = PricingSkill(api_url=api_url, country="ee")
prices = ps.fetch_electricity_prices()

vals = [p["price_eur_per_kwh"] for p in prices]

print("Number of prices:", len(vals))
print("Min:", min(vals))
print("Max:", max(vals))
print("30% quantile:", np.quantile(vals, 0.3))
print("70% quantile:", np.quantile(vals, 0.7))
print("\nAll prices:")
for v in vals:
    print(v)
