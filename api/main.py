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

import pandas as pd
from datetime import datetime
import os

@app.post("/predict")
def predict(data: InputData):
    try:
        input_dict = data.dict()

        # Convert to dataframe
        df = pd.DataFrame([input_dict])

        # Prediction
        prediction = model.predict(df)[0]

        # =========================
        # 🔥 LOGGING (IMPORTANT)
        # =========================
        log_data = {
            "timestamp": datetime.now(),
            "store_id": input_dict["store_id_enc"],
            "item_id": input_dict["item_id_enc"],
            "price": input_dict["price"],
            "discount_pct": input_dict["discount_pct"],
            "promotion": input_dict["promotion"],
            "lag_1": input_dict["lag_1"],
            "lag_7": input_dict["lag_7"],
            "predicted_demand": float(prediction)
        }

        log_df = pd.DataFrame([log_data])

        log_file = "logs/predictions.csv"

        # Create logs folder if not exists
        os.makedirs("logs", exist_ok=True)

        if os.path.exists(log_file):
            log_df.to_csv(log_file, mode='a', header=False, index=False)
        else:
            log_df.to_csv(log_file, index=False)

        return {"predicted_demand": float(prediction)}

    except Exception as e:
        return {"error": str(e)}
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