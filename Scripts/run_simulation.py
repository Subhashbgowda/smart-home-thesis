# scripts/run_simulation.py
import sys
import os

# Add project root to Python path so imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from agents.main_control_agent.skills.simulation_skill import SimulationSkill

if __name__ == "__main__":
    simulator = SimulationSkill(log_file="data/simulated_control_log.csv")
    simulator.simulate_data(cycles=25000, verbose=True)

