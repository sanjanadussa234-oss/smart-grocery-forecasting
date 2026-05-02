from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import json
import pandas as pd
import numpy as np
from datetime import datetime
import os

# =========================
# INIT APP
# =========================
app = FastAPI(title="Smart Grocery Demand Forecasting System")

# =========================
# LOAD MODEL + FEATURES
# =========================
model = joblib.load("models/xgboost_model.pkl")

with open("models/feature_columns.json", "r") as f:
    feature_columns = json.load(f)

print(f"✅ Model loaded with {len(feature_columns)} features")
print(f"Expected features: {feature_columns}")

# =========================
# INPUT SCHEMA (ONLY USER INPUTS)
# =========================
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

# =========================
# HEALTH CHECK
# =========================
@app.get("/")
def home():
    return {"message": "API running 🚀"}

# =========================
# PREDICT
# =========================
@app.post("/predict")
def predict(data: InputData):
    try:
        input_dict = data.dict()

        # =========================
        # CREATE EMPTY INPUT ROW (Initialize with zeros for ALL expected features)
        # =========================
        row = {col: 0 for col in feature_columns}

        # =========================
        # FILL USER INPUTS (Direct mapping)
        # =========================
        user_inputs = {
            "store_id_enc": input_dict["store_id_enc"],
            "item_id_enc": input_dict["item_id_enc"],
            "price": input_dict["price"],
            "base_price": input_dict["base_price"],
            "promotion": input_dict["promotion"],
            "discount_pct": input_dict["discount_pct"],
            "month": input_dict["month"],
            "day_of_week": input_dict["day_of_week"],
            "festival_flag": input_dict["festival_flag"],
            "weekend": input_dict["weekend"],
            "lag_1": input_dict["lag_1"],
            "lag_7": input_dict["lag_7"],
            "lag_14": input_dict["lag_14"],
            "rolling_mean_7": input_dict["rolling_mean_7"],
            "rolling_std_7": input_dict["rolling_std_7"],
        }
        
        row.update(user_inputs)

        # =========================
        # DERIVED FEATURES (Computed from user inputs)
        # =========================
        row["price_diff"] = row["base_price"] - row["price"]
        row["price_ratio"] = row["price"] / (row["base_price"] + 1e-5)
        row["promo_effect"] = row["promotion"] * row["discount_pct"]

        # =========================
        # TIME FEATURES (Context-based defaults)
        # =========================
        # If you want to use current date, uncomment below:
        # today = datetime.now()
        # row["year"] = today.year
        # row["month"] = today.month  # Override if needed
        
        row["year"] = 2026
        row["temperature_c"] = 25.0  # Default: can be made dynamic
        row["rainfall_mm"] = 0.0     # Default: can be made dynamic
        row["humidity_pct"] = 50.0   # Default: can be made dynamic

        # =========================
        # SEASON ENCODING (Based on month)
        # =========================
        m = int(row["month"])
        if m in [3, 4, 5]:
            row["season_enc"] = 1  # Spring
        elif m in [6, 7, 8]:
            row["season_enc"] = 2  # Summer
        elif m in [9, 10, 11]:
            row["season_enc"] = 3  # Fall
        else:
            row["season_enc"] = 4  # Winter

        # =========================
        # CYCLICAL ENCODING (Month & Day of Week)
        # =========================
        row["month_sin"] = np.sin(2 * np.pi * row["month"] / 12)
        row["month_cos"] = np.cos(2 * np.pi * row["month"] / 12)
        row["dow_sin"] = np.sin(2 * np.pi * row["day_of_week"] / 7)
        row["dow_cos"] = np.cos(2 * np.pi * row["day_of_week"] / 7)

        # =========================
        # CATEGORY FEATURES (One-hot encoded, default to 0)
        # =========================
        # If user provides category, set it to 1 (only one category should be 1)
        category_columns = [col for col in feature_columns if col.startswith("category_")]
        for col in category_columns:
            row[col] = 0  # Default: no category selected
        
        # Optional: If you want to accept category as input, modify InputData schema
        # For now, we default all categories to 0 (safe default)

        # =========================
        # VERIFY ALL FEATURES ARE PRESENT
        # =========================
        missing_cols = [col for col in feature_columns if col not in row]
        if missing_cols:
            return {"error": f"Missing features: {missing_cols}"}

        # =========================
        # CREATE DATAFRAME WITH CORRECT COLUMN ORDER
        # =========================
        df = pd.DataFrame([row])
        
        # Ensure columns match exactly (same order & names)
        df = df[feature_columns]

        # =========================
        # VALIDATION: Check dtypes match
        # =========================
        print(f"Features being sent to model: {list(df.columns)}")
        print(f"Shape: {df.shape}")

        # =========================
        # PREDICT
        # =========================
        prediction = model.predict(df)[0]

        # =========================
        # LOGGING
        # =========================
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "store_id": row["store_id_enc"],
            "item_id": row["item_id_enc"],
            "price": row["price"],
            "discount_pct": row["discount_pct"],
            "promotion": row["promotion"],
            "lag_1": row["lag_1"],
            "lag_7": row["lag_7"],
            "predicted_demand": float(prediction)
        }

        os.makedirs("logs", exist_ok=True)
        log_file = "logs/predictions.csv"

        log_df = pd.DataFrame([log_data])

        if os.path.exists(log_file):
            log_df.to_csv(log_file, mode="a", header=False, index=False)
        else:
            log_df.to_csv(log_file, index=False)

        return {
            "predicted_demand": float(prediction),
            "store_id": int(row["store_id_enc"]),
            "item_id": int(row["item_id_enc"]),
            "status": "success"
        }

    except Exception as e:
        import traceback
        print(f"❌ Error: {str(e)}")
        print(traceback.format_exc())
        return {"error": str(e), "status": "failed"}