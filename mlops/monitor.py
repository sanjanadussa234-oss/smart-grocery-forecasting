import pandas as pd
import numpy as np

# =========================
# LOAD DATA
# =========================
pred = pd.read_csv("logs/predictions.csv")
actual = pd.read_csv("logs/actuals.csv")

print("\n📊 DATA LOADED")

# =========================
# DATETIME
# =========================
pred["timestamp"] = pd.to_datetime(pred["timestamp"])
actual["timestamp"] = pd.to_datetime(actual["timestamp"])

pred["time_key"] = pred["timestamp"].dt.floor("h")
actual["time_key"] = actual["timestamp"].dt.floor("h")

# =========================
# MERGE
# =========================
merged = pd.merge(
    pred,
    actual,
    on=["store_id", "item_id", "time_key"],
    how="inner"
)

print(f"🔗 Merged records: {len(merged)}")

if len(merged) == 0:
    print("⚠️ No matching records")
    exit()

# =========================
# ERROR
# =========================
merged["error"] = merged["actual_sales"] - merged["predicted_demand"]
merged["abs_error"] = np.abs(merged["error"])

# =========================
# PERFORMANCE
# =========================
rmse = np.sqrt(np.mean(merged["error"] ** 2))
mae = np.mean(merged["abs_error"])

print("\n📈 MODEL PERFORMANCE")
print(f"RMSE: {rmse:.3f}")
print(f"MAE: {mae:.3f}")

# =========================
# AUTO RETRAIN TRIGGER
# =========================
import os

THRESHOLD = 10

if rmse > THRESHOLD:
    print("\n🚨 Triggering retraining pipeline...")
    os.system("python mlops/retrain.py")
else:
    print("\n✅ No retraining needed")

# =========================
# ROLLING RMSE (fixed)
# =========================
window = min(10, len(merged))  # avoids NaN issue
merged = merged.sort_values("timestamp_x")
merged = merged.drop(columns=["timestamp_x", "timestamp_y"])

merged["rolling_rmse"] = (
    merged["error"] ** 2
).rolling(window).mean().apply(np.sqrt)

latest_rmse = merged["rolling_rmse"].iloc[-1]

print("\n📉 DRIFT CHECK (ROLLING RMSE)")
print(f"Latest Rolling RMSE: {latest_rmse:.3f}")

# =========================
# FEATURE DRIFT CHECK
# =========================
print("\n📊 FEATURE DRIFT CHECK")

features = ["price", "discount_pct", "promotion", "lag_1", "lag_7"]

for col in features:
    if col in pred.columns:
        mean_val = pred[col].mean()
        std_val = pred[col].std()
        print(f"{col}: mean={mean_val:.2f}, std={std_val:.2f}")

# =========================
# ANOMALY DETECTION
# =========================
error_mean = merged["error"].mean()
error_std = merged["error"].std()

merged["z_score"] = (merged["error"] - error_mean) / error_std

anomalies = merged[np.abs(merged["z_score"]) > 3]

print("\n🚨 ANOMALY DETECTION")
print(f"Anomalies found: {len(anomalies)}")

# =========================
# TREND ANALYSIS
# =========================
print("\n📈 PREDICTION TREND")

trend = pred["predicted_demand"].tail(10).values

if len(trend) >= 2:
    if trend[-1] > trend[0]:
        print("⬆️ Demand increasing")
    elif trend[-1] < trend[0]:
        print("⬇️ Demand decreasing")
    else:
        print("➡️ Stable demand")

# =========================
# TOP ITEM ERROR
# =========================
print("\n📦 TOP ITEM ERROR")

top_items = (
    merged.groupby("item_id")
    .agg({"abs_error": "mean"})
    .sort_values("abs_error", ascending=False)
    .head(5)
)

print(top_items)