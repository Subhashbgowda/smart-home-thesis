import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the resampled dataset
df = pd.read_csv("data/smart_home_clean_minute.csv", parse_dates=["time"])

# ---------------------------
# 1. Overall house consumption over time
# ---------------------------
plt.figure(figsize=(12, 5))
plt.plot(df["time"], df["house_overall_kw"], label="House Overall (kW)")
plt.xlabel("Time")
plt.ylabel("Power (kW)")
plt.title("Overall House Electricity Consumption Over Time")
plt.legend()
plt.tight_layout()
plt.show()

# ---------------------------
# 2. Appliance contribution (stacked area plot)
# ---------------------------
appliances = ["dishwasher_kw", "fridge_kw", "microwave_kw", "livingroom_kw"]
plt.figure(figsize=(12, 5))
plt.stackplot(df["time"], df[appliances].T, labels=appliances)
plt.xlabel("Time")
plt.ylabel("Power (kW)")
plt.title("Appliance-wise Electricity Consumption")
plt.legend(loc="upper left")
plt.tight_layout()
plt.show()

# ---------------------------
# 3. Histogram of house consumption
# ---------------------------
plt.figure(figsize=(8, 5))
sns.histplot(df["house_overall_kw"], bins=50, kde=True, color="skyblue")
plt.xlabel("Power (kW)")
plt.title("Distribution of House Electricity Consumption")
plt.tight_layout()
plt.show()

# ---------------------------
# 4. Correlation heatmap (consumption vs weather)
# ---------------------------
cols_for_corr = ["house_overall_kw", "temp_c", "humidity", "pressure_hpa", "wind_speed", "cloud_cover"]
corr = df[cols_for_corr].apply(pd.to_numeric, errors="coerce").corr()  # ensure numeric
plt.figure(figsize=(8, 6))
sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Correlation between Consumption and Weather")
plt.tight_layout()
plt.show()

# ---------------------------
# 5. Scatter plot: consumption vs temperature
# ---------------------------
plt.figure(figsize=(8, 5))
plt.scatter(df["temp_c"], df["house_overall_kw"], alpha=0.3)
plt.xlabel("Temperature (°C)")
plt.ylabel("House Overall (kW)")
plt.title("House Consumption vs Temperature")
plt.tight_layout()
plt.show()

print("✅ Visualization complete. Check the plots for insights.")
