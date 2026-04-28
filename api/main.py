from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import json
import pandas as pd

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
    store_id_enc: float
    item_id_enc: float
    price: float
    base_price: float
    promotion: float
    discount_pct: float
    month: float
    day_of_week: float
    festival_flag: float
    weekend: float
    lag_1: float
    lag_7: float
    lag_14: float
    rolling_mean_7: float
    rolling_std_7: float
    price_diff: float
    price_ratio: float
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
@app.post("/predict")
def predict(data: InputData):

    df = pd.DataFrame([data.dict()])

    # align feature order (VERY IMPORTANT)
    df = df.reindex(columns=feature_columns, fill_value=0)

    prediction = model.predict(df)[0]

    return {
        "predicted_demand": float(prediction)
    }