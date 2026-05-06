# mlops/monitor.py

import pandas as pd
import numpy as np
import os

print("\n📊 MLOps Monitoring Started")


# =========================
# PIPELINES
# =========================
pipelines = [
    ("logs/single_predictions.csv", "logs/single_actuals.csv", "SINGLE"),
    ("logs/festival_predictions.csv", "logs/festival_actuals.csv", "FESTIVAL")
]


THRESHOLD = 10


# =========================
# PROCESS EACH PIPELINE
# =========================
for pred_path, actual_path, name in pipelines:

    if not os.path.exists(pred_path) or not os.path.exists(actual_path):
        print(f"⚠️ Missing files for {name}")
        continue

    print(f"\n🔍 Monitoring {name} pipeline")

    pred = pd.read_csv(pred_path)
    actual = pd.read_csv(actual_path)

    if len(pred) == 0 or len(actual) == 0:
        print("⚠️ Empty data")
        continue

    # -------------------------
    # Convert time
    # -------------------------
    pred["timestamp"] = pd.to_datetime(pred["timestamp"])
    actual["timestamp"] = pd.to_datetime(actual["timestamp"])

    pred["time_key"] = pred["timestamp"].dt.floor("h")
    actual["time_key"] = actual["timestamp"].dt.floor("h")

    # -------------------------
    # Merge
    # -------------------------
    merged = pd.merge(
        pred,
        actual,
        on=["store_id", "item_id", "time_key"],
        how="inner"
    )

    if len(merged) == 0:
        print("⚠️ No matching records")
        continue

    # -------------------------
    # ERROR METRICS
    # -------------------------
    merged["error"] = merged["actual_sales"] - merged["predicted_demand"]

    rmse = np.sqrt(np.mean(merged["error"] ** 2))
    mae = np.mean(np.abs(merged["error"]))

    print(f"\n📈 {name} PERFORMANCE")
    print(f"RMSE: {rmse:.3f}")
    print(f"MAE: {mae:.3f}")

    # -------------------------
    # DRIFT CHECK
    # -------------------------
    merged = merged.sort_values("timestamp")

    window = min(10, len(merged))

    merged["rolling_rmse"] = (
        merged["error"] ** 2
    ).rolling(window).mean().apply(np.sqrt)

    latest_rmse = merged["rolling_rmse"].iloc[-1]

    print(f"📉 Rolling RMSE: {latest_rmse:.3f}")

    # -------------------------
    # ANOMALY CHECK
    # -------------------------
    if merged["error"].std() != 0:
        z = (merged["error"] - merged["error"].mean()) / merged["error"].std()
        anomalies = merged[np.abs(z) > 3]
    else:
        anomalies = []

    print(f"🚨 Anomalies: {len(anomalies)}")

    # -------------------------
    # RETRAIN TRIGGER
    # -------------------------
    if rmse > THRESHOLD:
        print(f"🚨 Retraining triggered for {name}")
        os.system("python mlops/retrain.py")
    else:
        print(f"✅ {name} model is healthy")
    
    # =========================
    # DRIFT DECISION SIGNAL
    # =========================

    DRIFT_THRESHOLD = 10

    if rmse > DRIFT_THRESHOLD:
        print("\n🚨 DRIFT DETECTED → RETRAIN")
    else:
        print("\n✅ NO DRIFT → STABLE MODEL")