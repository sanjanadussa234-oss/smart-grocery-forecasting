import pandas as pd
import numpy as np
import os

# =========================
# CONFIG
# =========================
np.random.seed(42)

files = [
    ("logs/single_predictions.csv", "logs/single_actuals.csv"),
    ("logs/festival_predictions.csv", "logs/festival_actuals.csv")
]


# =========================
# PROCESS EACH FILE
# =========================
for pred_file, actual_file in files:

    if not os.path.exists(pred_file):
        print(f"⚠️ File not found: {pred_file}")
        continue

    print(f"\n📊 Processing {pred_file}")

    pred = pd.read_csv(pred_file)

    if len(pred) == 0:
        print("⚠️ Empty file, skipping")
        continue

    pred["timestamp"] = pd.to_datetime(pred["timestamp"])

    actuals = pred.copy()

    # -------------------------
    # Simulate actual sales
    # -------------------------
    actuals["actual_sales"] = actuals["predicted_demand"].apply(
        lambda x: max(0, x + np.random.normal(0, 8))
    )

    # -------------------------
    # time_key (CRITICAL FOR MLOPS)
    # -------------------------
    actuals["time_key"] = actuals["timestamp"].dt.floor("h")

    # -------------------------
    # Keep only required columns
    # -------------------------
    cols = [
    "timestamp",
    "time_key",
    "store_id",
    "item_id",
    "item_name",
    "category",
    "actual_sales"
]

    actuals = actuals[[c for c in cols if c in actuals.columns]]

    # -------------------------
    # SAVE
    # -------------------------
    actuals.to_csv(actual_file, index=False)

    print(f"✅ Saved: {actual_file}")