import csv
import random
from datetime import datetime, timedelta
import pytz

# ==========================================
# CONFIG
# ==========================================

CYCLES = 20000                 # ~3 months
INTERVAL_MINUTES = 10
TIMEZONE = "Europe/Bratislava"

RULE_LOG = "rule_eval_log.csv"
ML_LOG = "ml_eval_log.csv"

tz = pytz.timezone(TIMEZONE)

# Start 90 days ago
start_time = datetime.now(tz) - timedelta(days=90)

# ==========================================
# HELPERS
# ==========================================

def seasonal_temperature(day_index):
    """
    Simulate winter → spring transition.
    """
    base = -5 + (day_index * 0.2)   # slowly rising temp
    noise = random.uniform(-3, 3)
    return round(base + noise, 2)

def seasonal_price(hour, temperature):
    """
    High price during peak hours + cold weather spikes.
    """
    base = 0.09

    # peak hours expensive
    if 17 <= hour <= 21:
        base += 0.08

    # very cold = heating demand spike
    if temperature < 0:
        base += 0.05

    return round(base + random.uniform(-0.01, 0.01), 4)

def occupancy_pattern(hour):
    if 0 <= hour <= 6:
        return True
    if 8 <= hour <= 16:
        return False
    return True

# ==========================================
# CSV HEADERS
# ==========================================

headers = [
    "timestamp",
    "price_eur_per_kwh",
    "temperature",
    "humidity",
    "condition",
    "house_overall_kw",
    "occupied",
    "hour_of_day",
    "day_of_week",
    "is_weekend",
    "price_level",
    "comfort_mode",
    "action"
]

with open(RULE_LOG, "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerow(headers)

with open(ML_LOG, "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerow(headers)

print("Generating 3 months simulated dataset...")
print("Start:", start_time)

# ==========================================
# MAIN LOOP
# ==========================================

for i in range(CYCLES):

    ts = start_time + timedelta(minutes=i * INTERVAL_MINUTES)

    hour = ts.hour
    dow = ts.weekday()
    is_weekend = 1 if dow >= 5 else 0
    day_index = i // 144  # 144 cycles per day

    temperature = seasonal_temperature(day_index)
    price = seasonal_price(hour, temperature)
    occupied = occupancy_pattern(hour)

    humidity = random.randint(40, 95)

    if temperature < 0:
        condition = "Snow"
    elif temperature < 10:
        condition = "Clouds"
    else:
        condition = "Clear"

    # -------------------------
    # RULE CONTROLLER
    # -------------------------

    rule_load = random.uniform(1.5, 4.0)

    if not occupied:
        rule_action = "Turn off non-essential devices (unoccupied)"
        rule_load *= 0.6
    elif rule_load > 2.5:
        rule_action = "Reduce appliance usage (high load)"
    elif condition == "Clear":
        rule_action = "Good time to run appliances"
    else:
        rule_action = "Normal operation"

    # -------------------------
    # ML CONTROLLER
    # -------------------------

    ml_load = rule_load

    # ML reacts better to high prices
    if price > 0.18:
        ml_action = "Delay appliance usage (high price)"
        ml_load *= 0.55  # aggressive saving
    elif not occupied:
        ml_action = "Turn off non-essential devices (unoccupied)"
        ml_load *= 0.5
    elif ml_load > 2.5:
        ml_action = "Reduce appliance usage (smart optimization)"
        ml_load *= 0.8
    else:
        ml_action = "Normal operation"

    price_level = "low"
    if price > 0.16:
        price_level = "high"
    elif price > 0.11:
        price_level = "medium"

    # -------------------------
    # WRITE ROWS
    # -------------------------

    rule_row = [
        ts.isoformat(),
        price,
        temperature,
        humidity,
        condition,
        round(rule_load, 3),
        occupied,
        hour,
        dow,
        is_weekend,
        price_level,
        0,
        rule_action
    ]

    ml_row = [
        ts.isoformat(),
        price,
        temperature,
        humidity,
        condition,
        round(ml_load, 3),
        occupied,
        hour,
        dow,
        is_weekend,
        price_level,
        0,
        ml_action
    ]

    with open(RULE_LOG, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(rule_row)

    with open(ML_LOG, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(ml_row)

    if i % 1000 == 0:
        print(f"{i}/{CYCLES} cycles done")

print("Finished.")
print("Generated:")
print(" - rule_eval_log.csv")
print(" - ml_eval_log.csv")
