
import pandas as pd
import numpy as np
import joblib
import json
import mlflow
import mlflow.xgboost
from sklearn.metrics import mean_squared_error, mean_absolute_error
from xgboost import XGBRegressor
print("\n♻️ AUTO-RETRAINING TRIGGERED BY MLOPS PIPELINE")

# =========================
# SET MLFLOW EXPERIMENT
# =========================
mlflow.set_experiment("Grocery Demand Retraining")

# =========================
# LOAD DATA
# =========================
pred = pd.read_csv("logs/predictions.csv")
actual = pd.read_csv("logs/actuals.csv")

print("\n📊 DATA LOADED")

# =========================
# TIME ALIGNMENT
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

if len(merged) == 0:
    print("⚠️ No data for retraining")
    exit()

# =========================
# ERROR CHECK
# =========================
merged["error"] = merged["actual_sales"] - merged["predicted_demand"]

rmse = np.sqrt(np.mean(merged["error"] ** 2))
mae = np.mean(np.abs(merged["error"]))

print(f"\n📉 Current RMSE: {rmse:.3f}")
print(f"📉 Current MAE: {mae:.3f}")

# =========================
# RETRAIN CONDITION
# =========================
THRESHOLD = 10

if rmse < THRESHOLD:
    print("✅ Model is good. No retraining needed.")
    exit()

print("🚨 Retraining model...")

# =========================
# LOAD FULL DATASET
# =========================
data = pd.read_csv("data/new_featured/featured_data.csv")

# =========================
# FEATURES
# =========================
with open("models/feature_columns.json", "r") as f:
    feature_columns = json.load(f)

X = data[feature_columns]
y = data["sales_units"]

# =========================
# TRAIN + LOG WITH MLFLOW
# =========================
with mlflow.start_run():

    model = XGBRegressor(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1
    )

    model.fit(X, y)

    # =========================
    # PREDICT ON TRAIN DATA (for tracking)
    # =========================
    preds = model.predict(X)

    train_rmse = np.sqrt(mean_squared_error(y, preds))
    train_mae = mean_absolute_error(y, preds)

    # =========================
    # LOG PARAMETERS
    # =========================
    mlflow.log_param("n_estimators", 100)
    mlflow.log_param("max_depth", 6)
    mlflow.log_param("learning_rate", 0.1)

    # =========================
    # LOG METRICS
    # =========================
    mlflow.log_metric("train_rmse", train_rmse)
    mlflow.log_metric("train_mae", train_mae)
    mlflow.log_metric("production_rmse", rmse)
    mlflow.log_metric("production_mae", mae)

    # =========================
    # LOG MODEL
    # =========================
    mlflow.xgboost.log_model(model, "model")

    # =========================
    # SAVE MODEL LOCALLY
    # =========================
    # joblib.dump(model, "models/xgboost_model.pkl")
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_path = f"models/xgboost_{timestamp}.pkl"

    joblib.dump(model, model_path)

    # Optional: update latest pointer
    joblib.dump(model, "models/xgboost_latest.pkl")

    print("✅ Model retrained and saved!")
    print(f"📊 Train RMSE: {train_rmse:.3f}")