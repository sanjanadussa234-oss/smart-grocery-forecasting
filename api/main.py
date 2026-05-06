# api/main.py

from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import pandas as pd
import os
import threading
from mlops.pipeline_runner import run_pipeline

from src.predict import predict_demand, predict_festival_demand

app = FastAPI(title="Smart Grocery Demand Forecasting System")


# =========================
# REQUEST SCHEMAS
# =========================

class SingleItemRequest(BaseModel):
    item_name: str
    category: str
    store_id: int
    current_stock: float

    is_festival: bool = False
    festival_name: str = "none"

    has_discount: bool = False
    discount_pct: float = 0

    has_promotion: bool = False
    promotion: int = 0


class FestivalRequest(BaseModel):
    festival_name: str
    store_id: int
    top_n: int = 5

    has_discount: bool = False
    discount_pct: float = 0

    has_promotion: bool = False
    promotion: int = 0


# =========================
# HEALTH CHECK
# =========================
@app.get("/")
def home():
    return {"message": "API running 🚀"}


# =========================
# SINGLE ITEM PREDICTION
# =========================
@app.post("/predict")
def predict_single(data: SingleItemRequest):

    result = predict_demand(
        item_name=data.item_name,
        category=data.category,
        store_id=data.store_id,
        current_stock=data.current_stock,

        is_festival=data.is_festival,
        festival_name=data.festival_name,

        has_discount=data.has_discount,
        discount_pct=data.discount_pct,

        has_promotion=data.has_promotion,
        promotion=data.promotion
    )

    # -------------------------
    # LOG SINGLE PREDICTIONS
    # -------------------------
    os.makedirs("logs", exist_ok=True)

    log_file = "logs/single_predictions.csv"

    log_data = {
        "timestamp": datetime.now().isoformat(),
        "store_id": data.store_id,
        "item_id": result.get("item_id"),
        "item_name": data.item_name,
        "category": data.category,
        "price": result.get("price", 0),
        "discount_pct": data.discount_pct,
        "promotion": data.promotion,
        "lag_1": result.get("lag_1", 0),
        "lag_7": result.get("lag_7", 0),
        "predicted_demand": result.get("predicted_demand")
    }

    df = pd.DataFrame([log_data])

    if os.path.exists(log_file):
        df.to_csv(log_file, mode="a", header=False, index=False)
    else:
        df.to_csv(log_file, index=False)
    # 🚀 RUN MLOPS PIPELINE IN BACKGROUND
    threading.Thread(target=run_pipeline).start()

    return result


# =========================
# FESTIVAL PREDICTION
# =========================
@app.post("/predict/festival")
def predict_festival(data: FestivalRequest):

    result = predict_festival_demand(
        festival_name=data.festival_name,
        store_id=data.store_id,
        top_n=data.top_n,
        has_discount=data.has_discount,
        discount_pct=data.discount_pct,
        has_promotion=data.has_promotion,
        promotion=data.promotion
    )

    # =========================
    # LOG FESTIVAL PREDICTIONS
    # =========================
    os.makedirs("logs", exist_ok=True)

    log_file = "logs/festival_predictions.csv"

    rows = []

    for item in result:   # result is LIST (important!)
        rows.append({
            "timestamp": datetime.now().isoformat(),
            "store_id": data.store_id,
            "item_id": item.get("item_id"),
            "item_name": item.get("item_name"),
            "category": item.get("category"),
            "festival": data.festival_name,
            "predicted_demand": item.get("predicted_demand"),
            "discount_pct": data.discount_pct,
            "promotion": data.promotion
        })

    df = pd.DataFrame(rows)

    if os.path.exists(log_file):
        df.to_csv(log_file, mode="a", header=False, index=False)
    else:
        df.to_csv(log_file, index=False)

    return result