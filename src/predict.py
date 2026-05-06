# src/predict.py

import pandas as pd
import numpy as np
import joblib

# -------------------------
# Paths (UPDATE MODEL NAME IF NEEDED)
# -------------------------
MODEL_PATH = "models/Xgboost_20260505_181142.pkl"

ITEM_ENCODER_PATH = "data/new_featured/item_encoder.pkl"
CATEGORY_ENCODER_PATH = "data/new_featured/category_encoder.pkl"
FESTIVAL_ENCODER_PATH = "data/new_featured/festival_encoder.pkl"

MAPPING_PATH = "data/new_processed/item_mapping.csv"
FEATURE_DATA_PATH = "data/new_featured/featured_data.csv"


# -------------------------
# Load artifacts
# -------------------------
print("🔄 Loading model and encoders...")

model = joblib.load(MODEL_PATH)

item_encoder = joblib.load(ITEM_ENCODER_PATH)
category_encoder = joblib.load(CATEGORY_ENCODER_PATH)
festival_encoder = joblib.load(FESTIVAL_ENCODER_PATH)

item_mapping = pd.read_csv(MAPPING_PATH)
feature_df = pd.read_csv(FEATURE_DATA_PATH)


# -------------------------
# Helper: Get lag features
# -------------------------
def get_latest_lags(store_id, item_encoded):

    df_filtered = feature_df[
        (feature_df['store_id'] == store_id) &
        (feature_df['item_encoded'] == item_encoded)
    ]

    if len(df_filtered) == 0:
        return 0, 0, 0

    last_row = df_filtered.iloc[-1]

    return (
        last_row['lag_1'],
        last_row['lag_7'],
        last_row['rolling_mean_7']
    )


# -------------------------
# Single Item Prediction
# -------------------------
def predict_demand(
    item_name,
    category,
    store_id,
    current_stock,

    # Business Inputs
    is_festival=False,
    festival_name="none",

    has_discount=False,
    discount_pct=0,

    has_promotion=False,
    promotion=0,

    # Optional Inputs
    price=100,
    base_price=100,

    day_of_week=2,
    month=5,
    weekofyear=20,

    temperature_c=25,
    rainfall_mm=0,
    humidity_pct=50
):

    # Normalize inputs
    item_name = item_name.lower()
    category = category.lower()
    festival_name = festival_name.lower()

    # Business logic
    if not is_festival:
        festival_name = "none"

    if not has_discount:
        discount_pct = 0

    if not has_promotion:
        promotion = 0

    # Get item_id
    item_row = item_mapping[item_mapping['item_name'] == item_name]

    if item_row.empty:
        return {"error": f"Item '{item_name}' not found"}

    item_id = item_row.iloc[0]['item_id']

    # Encode inputs
    try:
        item_encoded = item_encoder.transform([item_id])[0]
        category_encoded = category_encoder.transform([category])[0]
        festival_encoded = festival_encoder.transform([festival_name])[0]
    except Exception as e:
        return {"error": f"Encoding failed: {str(e)}"}

    # Get lag features
    lag_1, lag_7, rolling_mean_7 = get_latest_lags(store_id, item_encoded)

    # Create input
    input_data = pd.DataFrame([{
        'store_id': store_id,
        'item_encoded': item_encoded,
        'category_encoded': category_encoded,
        'festival_encoded': festival_encoded,
        'price': price,
        'base_price': base_price,
        'discount_pct': discount_pct,
        'promotion': promotion,
        'day_of_week': day_of_week,
        'month': month,
        'weekofyear': weekofyear,
        'lag_1': lag_1,
        'lag_7': lag_7,
        'rolling_mean_7': rolling_mean_7,
        'temperature_c': temperature_c,
        'rainfall_mm': rainfall_mm,
        'humidity_pct': humidity_pct
    }])

    # Predict
    predicted_demand = model.predict(input_data)[0]

    # Stock-aware logic
    recommended_order = max(predicted_demand - current_stock, 0)

    return {
        "item_name": item_name,
        "item_id": item_id,
        "category": category,
        "store_id": store_id,
        "festival": festival_name,
        "predicted_demand": round(float(predicted_demand), 2),
        "current_stock": current_stock,
        "recommended_order_quantity": round(float(recommended_order), 2)
    }


# -------------------------
# Festival-Based Prediction
# -------------------------
def predict_festival_demand(
    festival_name,
    store_id,
    top_n=5,

    has_discount=False,
    discount_pct=0,

    has_promotion=False,
    promotion=0
):

    festival_name = festival_name.lower()

    print(f"\n🎉 Predicting for festival: {festival_name}")

    # Encode festival
    try:
        festival_encoded = festival_encoder.transform([festival_name])[0]
    except:
        return {"error": f"Festival '{festival_name}' not found"}

    # Filter dataset
    df_festival = feature_df[
        feature_df['festival_encoded'] == festival_encoded
    ]

    if df_festival.empty:
        return {"error": f"No data for festival '{festival_name}'"}

    # Get top items
    top_items = (
        df_festival.groupby('item_encoded')['sales_units']
        .mean()
        .sort_values(ascending=False)
        .head(top_n)
        .index
    )

    results = []

    for item_encoded in top_items:

        # Decode item
        item_id = item_encoder.inverse_transform([item_encoded])[0]
        item_row = item_mapping[item_mapping['item_id'] == item_id]

        item_name = item_row.iloc[0]['item_name']
        category = item_row.iloc[0]['category']

        # Predict
        result = predict_demand(
            item_name=item_name,
            category=category,
            store_id=store_id,
            current_stock=0,

            is_festival=True,
            festival_name=festival_name,

            has_discount=has_discount,
            discount_pct=discount_pct,

            has_promotion=has_promotion,
            promotion=promotion
        )

        if "error" not in result:

        # Remove stock-related fields for festival view
         result.pop("current_stock", None)
         result.pop("recommended_order_quantity", None)

         results.append(result)

    # Sort results
    results = sorted(results, key=lambda x: x['predicted_demand'], reverse=True)

    return results


# -------------------------
# TEST
# -------------------------
if __name__ == "__main__":

    print("\n📊 Single Item Prediction:")
    result = predict_demand(
        item_name="tomato",
        category="vegetables",
        store_id=1,
        current_stock=100,

        is_festival=True,
        festival_name="new year",

        has_discount=True,
        discount_pct=20,

        has_promotion=True,
        promotion=1
    )
    print(result)

    print("\n🎉 Festival Prediction:")
    festival_result = predict_festival_demand(
        festival_name="new year",
        store_id=1,
        top_n=5,
        has_discount=True,
        discount_pct=10,
        has_promotion=True
    )

    for item in festival_result:
        print(item)