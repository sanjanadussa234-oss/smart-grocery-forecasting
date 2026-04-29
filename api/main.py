from fastapi import FastAPI
from pydantic import BaseModel, Field
import joblib
import json
import pandas as pd
import csv
from datetime import datetime
import os
# -----------------------
# LOAD MODEL
# -----------------------
model = joblib.load("models/xgboost_model.pkl")

# -----------------------
# LOAD FEATURE COLUMNS
# -----------------------
with open("models/feature_columns.json", "r") as f:
    feature_columns = json.load(f)

# -----------------------
# INIT APP
# -----------------------
app = FastAPI(title="Smart Grocery Demand Forecasting System")


# -----------------------
# INPUT SCHEMA
# -----------------------
class InputData(BaseModel):
    store_id_enc: float = Field(..., ge=0)
    item_id_enc: float = Field(..., ge=0)

    price: float = Field(..., gt=0)
    base_price: float = Field(..., gt=0)

    promotion: float = Field(..., ge=0, le=1)
    discount_pct: float = Field(..., ge=0, le=100)

    month: float = Field(..., ge=1, le=12)
    day_of_week: float = Field(..., ge=0, le=6)

    festival_flag: float = Field(..., ge=0, le=1)
    weekend: float = Field(..., ge=0, le=1)

    lag_1: float = Field(..., ge=0)
    lag_7: float = Field(..., ge=0)
    lag_14: float = Field(..., ge=0)

    rolling_mean_7: float = Field(..., ge=0)
    rolling_std_7: float = Field(..., ge=0)

    price_diff: float
    price_ratio: float = Field(..., gt=0)

    promo_effect: float

    month_sin: float
    month_cos: float
    dow_sin: float
    dow_cos: float


# -----------------------
# HEALTH CHECK
# -----------------------
@app.get("/")
def home():
    return {"message": "Grocery Demand Forecasting API is running 🚀"}


# -----------------------
# PREDICTION ENDPOINT
# -----------------------
from fastapi import HTTPException

@app.post("/predict")
def predict(data: InputData):
    try:
        df = pd.DataFrame([data.dict()])

        # align feature order
        df = df.reindex(columns=feature_columns, fill_value=0)

        prediction = model.predict(df)[0]

        # logging
        log_prediction(
            store_id=data.store_id_enc,
            item_id=data.item_id_enc,
            prediction=float(prediction),
            input_data=data.dict()
        )

        return {
            "predicted_demand": float(prediction)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )
def log_prediction(store_id, item_id, prediction, input_data):
    os.makedirs("logs", exist_ok=True)

    file_path = "logs/predictions.csv"
    file_exists = os.path.isfile(file_path)

    with open(file_path, mode="a", newline="") as f:
        writer = csv.writer(f)

        # header (updated)
        if not file_exists:
            writer.writerow([
                "timestamp",
                "store_id",
                "item_id",
                "price",
                "discount_pct",
                "promotion",
                "lag_1",
                "lag_7",
                "predicted_demand"
            ])

        writer.writerow([
            datetime.now(),
            store_id,
            item_id,
            input_data["price"],
            input_data["discount_pct"],
            input_data["promotion"],
            input_data["lag_1"],
            input_data["lag_7"],
            prediction
        ])