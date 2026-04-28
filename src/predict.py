import joblib
import pandas as pd
import json

# --------------------------
# LOAD MODEL
# --------------------------
model = joblib.load("models/xgboost_model.pkl")

# --------------------------
# LOAD FEATURE COLUMNS
# --------------------------
with open("models/feature_columns.json", "r") as f:
    feature_columns = json.load(f)


# --------------------------
# PREDICTION FUNCTION
# --------------------------
def predict_demand(input_data):
    """
    input_data: dictionary of one row features
    """

    df = pd.DataFrame([input_data])

    # align columns EXACTLY like training
    df = df.reindex(columns=feature_columns, fill_value=0)

    prediction = model.predict(df)

    return float(prediction[0])


# --------------------------
# TEST RUN (VERY IMPORTANT)
# --------------------------
if __name__ == "__main__":

    sample_input = {
        "store_id_enc": 1,
        "item_id_enc": 2,
        "price": 20,
        "base_price": 25,
        "promotion": 1,
        "discount_pct": 10,
        "month": 4,
        "day_of_week": 2,
        "festival_flag": 0,
        "weekend": 0,
        "lag_1": 10,
        "lag_7": 12,
        "lag_14": 11,
        "rolling_mean_7": 11.5,
        "rolling_std_7": 1.2,
        "price_diff": 5,
        "price_ratio": 0.8,
        "promo_effect": 10,
        "month_sin": 0.5,
        "month_cos": 0.8,
        "dow_sin": 0.2,
        "dow_cos": 0.9
    }

    result = predict_demand(sample_input)

    print("🔥 Predicted Demand:", result)