import pandas as pd
import datetime

# Load raw dataset safely
df = pd.read_csv("data/smart_home_raw.csv", low_memory=False, on_bad_lines="skip")

# 1. Convert timestamp (Unix → datetime) safely
df["time"] = pd.to_numeric(df["time"], errors="coerce")  # invalid → NaN
df = df.dropna(subset=["time"])  # drop rows with bad timestamps
df["time"] = pd.to_datetime(df["time"], unit="s")

# 2. Select useful columns
columns_to_keep = [
    "time",
    "House overall [kW]",
    "Dishwasher [kW]",
    "Fridge [kW]",
    "Microwave [kW]",
    "Living room [kW]",
    "temperature",
    "humidity",
    "pressure",
    "windSpeed",
    "cloudCover"
]
df = df[columns_to_keep]

# 3. Rename columns
df.rename(columns={
    "House overall [kW]": "house_overall_kw",
    "Dishwasher [kW]": "dishwasher_kw",
    "Fridge [kW]": "fridge_kw",
    "Microwave [kW]": "microwave_kw",
    "Living room [kW]": "livingroom_kw",
    "temperature": "temp_c",
    "humidity": "humidity",
    "pressure": "pressure_hpa",
    "windSpeed": "wind_speed",
    "cloudCover": "cloud_cover"
}, inplace=True)

# 4. Handle missing values
df = df.dropna()
# Convert cloud_cover to numeric

df["cloud_cover"] = pd.to_numeric(df["cloud_cover"], errors="coerce")
df = df.dropna(subset=["cloud_cover"])  # drop rows where conversion failed


# 5. Save cleaned dataset
df.to_csv("data/smart_home_clean.csv", index=False)

print("  Cleaning complete. Saved as data/smart_home_clean.csv")
print(df.head())
