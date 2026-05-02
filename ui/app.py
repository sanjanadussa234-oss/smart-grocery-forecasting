import streamlit as st
import requests
import pandas as pd

API_URL = "https://smart-grocery-api-edob.onrender.com/predict"

st.title("🛒 Smart Grocery Demand Forecasting System")

# =========================
# 🔮 PREDICTION SECTION (RESTORED)
# =========================

st.subheader("Enter Product Details")

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

    try:
        response = requests.post(API_URL, json=payload)

        if response.status_code == 200:
            result = response.json()
            prediction = result["predicted_demand"]

            st.success(f"Predicted Demand: {prediction:.2f}")

        else:
            st.error(response.text)

    except Exception as e:
        st.error(f"Connection Error: {e}")

# =========================
# 📊 DYNAMIC ANALYTICS
# =========================

st.subheader("📊 Dynamic Demand Analytics")

try:
    df = pd.read_csv("logs/predictions.csv")

    if df.empty:
        st.warning("No prediction data available yet.")
    else:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Fix data types
        df["store_id"] = df["store_id"].astype(int)
        df["item_id"] = df["item_id"].astype(int)

        # =========================
        # 🔎 FILTERS
        # =========================
        st.sidebar.header("🔎 Filters")

        store_options = ["All"] + sorted(df["store_id"].unique().tolist())
        item_options = ["All"] + sorted(df["item_id"].unique().tolist())

        store_filter = st.sidebar.selectbox("Select Store", store_options)
        item_filter = st.sidebar.selectbox("Select Item", item_options)

        date_range = st.sidebar.date_input(
            "Select Date Range",
            [df["timestamp"].min(), df["timestamp"].max()]
        )

        # =========================
        # 🧹 APPLY FILTERS
        # =========================
        filtered_df = df.copy()

        if store_filter != "All":
            filtered_df = filtered_df[filtered_df["store_id"] == int(store_filter)]

        if item_filter != "All":
            filtered_df = filtered_df[filtered_df["item_id"] == int(item_filter)]

        if len(date_range) == 2:
            start = pd.to_datetime(date_range[0])
            end = pd.to_datetime(date_range[1])
            filtered_df = filtered_df[
                (filtered_df["timestamp"] >= start) &
                (filtered_df["timestamp"] <= end)
            ]

        # =========================
        # 📊 METRICS
        # =========================
        st.subheader("📊 Summary")

        if len(filtered_df) > 0:
            col1, col2, col3 = st.columns(3)

            col1.metric("Latest", round(filtered_df["predicted_demand"].iloc[-1], 2))
            col2.metric("Average", round(filtered_df["predicted_demand"].mean(), 2))
            col3.metric("Max", round(filtered_df["predicted_demand"].max(), 2))
        else:
            st.warning("No data for selected filters")

        # =========================
        # 📈 CHART
        # =========================
        st.subheader("📈 Demand Trend")

        if len(filtered_df) > 0:
            st.line_chart(filtered_df.set_index("timestamp")["predicted_demand"])
        else:
            st.info("Adjust filters to see data")

        # =========================
        # 📋 TABLE
        # =========================
        st.subheader("📋 Data")

        st.dataframe(filtered_df.tail(10))

except Exception as e:
    st.error(f"Error loading data: {e}")