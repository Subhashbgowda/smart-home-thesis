from agents.electricity_agent.skills.consumption_skills import ElectricitySkill
import json
import time

if __name__ == "__main__":
    electricity_skill = ElectricitySkill()

    while True:
        consumption = electricity_skill.get_current_consumption()
        if consumption is None:
            print("⚠️ Reached end of CSV dataset.")
            break  # end of CSV

        # Convert timestamp to string for JSON
        consumption["timestamp"] = consumption["timestamp"].isoformat()
        print(json.dumps(consumption, indent=4))

        # Wait 60 seconds to simulate real-time minute-wise data
        time.sleep(60)
