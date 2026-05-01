import datetime
from agents.pricing_agent.skills.pricing_skill import PricingSkill


if __name__ == "__main__":
    today = datetime.date.today()
    start = today.strftime("%Y-%m-%dT00:00:00Z")
    end   = today.strftime("%Y-%m-%dT23:59:59Z")

    api_url = f"https://dashboard.elering.ee/api/nps/price?start={start}&end={end}"

    skill = PricingSkill(api_url, country="ee")  # Estonia
    print(skill.generate_report())
