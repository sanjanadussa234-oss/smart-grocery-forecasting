import streamlit as st
import requests

# =========================
# CONFIG
# =========================
API_URL = "https://smart-grocery-api-edob.onrender.com/predict"

st.title("🛒 Smart Grocery Demand Forecasting System")
st.write("Enter product details to predict demand")

# =========================
# INPUTS
# =========================
store_id = st.number_input("Store ID", min_value=0)
item_id = st.number_input("Item ID", min_value=0)
price = st.number_input("Price", min_value=0.0)
base_price = st.number_input("Base Price", min_value=0.0)
promotion = st.number_input("Promotion (0/1)", min_value=0, max_value=1)
discount = st.number_input("Discount %", min_value=0.0)

lag_1 = st.number_input("Lag 1", min_value=0.0)
lag_7 = st.number_input("Lag 7", min_value=0.0)
lag_14 = st.number_input("Lag 14", min_value=0.0)

# =========================
# PREDICTION BUTTON
# =========================
if st.button("Predict Demand"):

    # prevent division error
    safe_base_price = base_price if base_price != 0 else 1

    payload = {
        "store_id_enc": float(store_id),
        "item_id_enc": float(item_id),
        "price": float(price),
        "base_price": float(base_price),
        "promotion": float(promotion),
        "discount_pct": float(discount),
        "month": 4,
        "day_of_week": 2,
        "festival_flag": 0,
        "weekend": 0,
        "lag_1": float(lag_1),
        "lag_7": float(lag_7),
        "lag_14": float(lag_14),
        "rolling_mean_7": 0.0,
        "rolling_std_7": 0.0,
        "price_diff": float(base_price - price),
        "price_ratio": float(price / safe_base_price),
        "promo_effect": float(promotion * discount),
        "month_sin": 0.0,
        "month_cos": 0.0,
        "dow_sin": 0.0,
        "dow_cos": 0.0
    }

    try:
        response = requests.post(API_URL, json=payload, timeout=10)

        if response.status_code == 200:
            result = response.json()

            # handle both possible keys
            prediction = result.get("prediction") or result.get("predicted_demand")

            st.success(f"📈 Predicted Demand: {prediction:.2f}")

        else:
            st.error(f"❌ API Error: {response.text}")

    except requests.exceptions.RequestException as e:
        st.error(f"🚨 Connection Error: {e}")