# src/train.py

import pandas as pd
import numpy as np
import os
from datetime import datetime

import mlflow
import mlflow.xgboost

from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, r2_score


# -------------------------------
# CONFIG
# -------------------------------
MODEL_NAME = "XGBoost"
VERSION = "v1"


# -------------------------------
# MAIN FUNCTION
# -------------------------------
def train_xgboost():

    mlflow.set_tracking_uri("file:./mlruns")
    mlflow.set_experiment("Grocery")

    run_name = f"{MODEL_NAME}_{VERSION}"

    print("📥 Loading dataset...")
    df = pd.read_csv("data/new_featured/featured_data.csv")

    # -------------------------------
    # FEATURES & TARGET
    # -------------------------------
    FEATURE_COLUMNS = [
        'store_id',
        'item_encoded',
        'category_encoded',
        'festival_encoded',
        'price',
        'base_price',
        'discount_pct',
        'promotion',
        'day_of_week',
        'month',
        'weekofyear',
        'lag_1',
        'lag_7',
        'rolling_mean_7',
        'temperature_c',
        'rainfall_mm',
        'humidity_pct'
    ]

    TARGET = 'sales_units'

    X = df[FEATURE_COLUMNS]
    y = df[TARGET]

    # -------------------------------
    # TRAIN-TEST SPLIT (Time-based)
    # -------------------------------
    split = int(len(df) * 0.8)

    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    print(f"Training size: {len(X_train)}")
    print(f"Testing size: {len(X_test)}")

    # -------------------------------
    # MODEL
    # -------------------------------
    model = XGBRegressor(
        n_estimators=200,
        learning_rate=0.1,
        max_depth=6,
        random_state=42
    )

    print("\n🚀 Training XGBoost...")

    # -------------------------------
    # MLflow RUN
    # -------------------------------
    with mlflow.start_run(run_name=run_name):

        # Log params
        mlflow.log_param("model_name", MODEL_NAME)
        mlflow.log_param("version", VERSION)
        mlflow.log_param("n_estimators", 200)
        mlflow.log_param("learning_rate", 0.1)
        mlflow.log_param("max_depth", 6)

        # -------------------------------
        # TRAIN
        # -------------------------------
        model.fit(X_train, y_train)

        # -------------------------------
        # PREDICT
        # -------------------------------
        y_pred = model.predict(X_test)

        # -------------------------------
        # METRICS
        # -------------------------------
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)

        print("\n📈 XGBoost Performance:")
        print("RMSE:", round(rmse, 3))
        print("R2:", round(r2, 3))

        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2_score", r2)

        # -------------------------------
        # LOG MODEL IN MLflow
        # -------------------------------
        mlflow.xgboost.log_model(
            model,
            artifact_path="xgboost_model"
        )

        # -------------------------------
        # SAVE LOCALLY (NO OVERWRITE)
        # -------------------------------
        os.makedirs("models", exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_path = f"models/Xgboost_{timestamp}.pkl"

        import joblib
        joblib.dump(model, model_path)

        print(f"\n💾 Model saved locally: {model_path}")
        print(f"✅ {run_name} logged in MLflow")


# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    train_xgboost()