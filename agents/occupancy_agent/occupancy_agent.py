import time
import json
from agents.occupancy_agent.skills.occupancy_skill import OccupancySkill

if __name__ == "__main__":
    skill = OccupancySkill()

    while True:
        status = skill.get_next_status()
        print(json.dumps(status, indent=4))
        time.sleep(5)  # run every 5 seconds
