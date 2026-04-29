import streamlit as st
import requests

st.title("🛒 Smart Grocery Demand Forecasting System")

st.write("Enter product details to predict demand")

store_id = st.number_input("Store ID", 0)
item_id = st.number_input("Item ID", 0)
price = st.number_input("Price", 0.0)
base_price = st.number_input("Base Price", 0.0)
promotion = st.number_input("Promotion (0/1)", 0)
discount = st.number_input("Discount %", 0.0)

lag_1 = st.number_input("Lag 1", 0.0)
lag_7 = st.number_input("Lag 7", 0.0)
lag_14 = st.number_input("Lag 14", 0.0)

if st.button("Predict Demand"):

    payload = {
        "store_id_enc": store_id,
        "item_id_enc": item_id,
        "price": price,
        "base_price": base_price,
        "promotion": promotion,
        "discount_pct": discount,
        "month": 4,
        "day_of_week": 2,
        "festival_flag": 0,
        "weekend": 0,
        "lag_1": lag_1,
        "lag_7": lag_7,
        "lag_14": lag_14,
        "rolling_mean_7": 0,
        "rolling_std_7": 0,
        "price_diff": base_price - price,
        "price_ratio": price / (base_price + 1e-5),
        "promo_effect": promotion * discount,
        "month_sin": 0,
        "month_cos": 0,
        "dow_sin": 0,
        "dow_cos": 0
    }

    response = requests.post("http://127.0.0.1:8000/predict", json=payload)

    st.success(f"Predicted Demand: {response.json()['predicted_demand']}")