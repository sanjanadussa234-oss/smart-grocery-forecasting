import pandas as pd
import numpy as np

# =========================
# LOAD PREDICTIONS
# =========================
pred = pd.read_csv("logs/predictions.csv")

# Convert timestamp properly
pred["timestamp"] = pd.to_datetime(pred["timestamp"])

# =========================
# SIMULATE ACTUAL SALES
# =========================
np.random.seed(42)

actuals = pred.copy()

# Add realistic noise (+/- demand variation)
actuals["actual_sales"] = actuals["predicted_demand"].apply(
    lambda x: max(0, x + np.random.normal(0, 8))
)

# =========================
# IMPORTANT FIX
# =========================
# Create SAME time_key as monitor.py
actuals["time_key"] = actuals["timestamp"].dt.floor("h")

# Keep only required columns
actuals = actuals[[
    "timestamp",
    "time_key",
    "store_id",
    "item_id",
    "actual_sales"
]]

# =========================
# SAVE FILE
# =========================
actuals.to_csv("logs/actuals.csv", index=False)

print("✅ actuals.csv created successfully")