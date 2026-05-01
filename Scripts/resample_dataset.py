import pandas as pd

df = pd.read_csv("data/smart_home_clean.csv", parse_dates=["time"])
df.set_index("time", inplace=True)

# Resample per minute
df_minute = df.resample("1T").mean().reset_index()

df_minute.to_csv("data/smart_home_clean_minute.csv", index=False)
print(df_minute.head())
