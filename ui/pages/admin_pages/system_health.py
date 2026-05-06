# ui/pages/admin_pages/system_health.py

import streamlit as st
import pandas as pd
from pathlib import Path

MONITORING_FILE = Path(__file__).parent.parent.parent / "data" / "monitoring.csv"
ORDERS_FILE = Path(__file__).parent.parent.parent / "data" / "orders.csv"
USERS_FILE = Path(__file__).parent.parent.parent / "data" / "users.csv"


def safe_read(path):
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except:
        return pd.DataFrame()


def show():
    st.title("🏥 System Health Dashboard")

    monitoring_df = safe_read(MONITORING_FILE)
    orders_df = safe_read(ORDERS_FILE)
    users_df = safe_read(USERS_FILE)

    # =========================
    # SYSTEM METRICS
    # =========================
    st.subheader("📊 Overall System Metrics")

    col1, col2, col3 = st.columns(3)

    with col1:
        total_predictions = len(monitoring_df)
        st.metric("Total Predictions", total_predictions)

    with col2:
        total_orders = len(orders_df)
        st.metric("Total Orders", total_orders)

    with col3:
        total_users = len(users_df)
        st.metric("Total Users", total_users)

    # =========================
    # DRIFT ANALYSIS
    # =========================
    st.divider()
    st.subheader("🔍 Drift Analysis")

    if not monitoring_df.empty and "drift_detected" in monitoring_df.columns:
        drift_count = monitoring_df["drift_detected"].sum()
        st.metric("Drift Events", int(drift_count))
    else:
        st.info("No drift data available")

    # =========================
    # RETRAINING ANALYSIS
    # =========================
    st.divider()
    st.subheader("🔁 Retraining Analysis")

    if not monitoring_df.empty and "retrained" in monitoring_df.columns:
        retrain_count = monitoring_df["retrained"].sum()
        st.metric("Total Retraining Runs", int(retrain_count))
    else:
        st.info("No retraining data available")

    # =========================
    # ORDER STATUS
    # =========================
    st.divider()
    st.subheader("📦 Order Status Overview")

    if not orders_df.empty and "status" in orders_df.columns:
        status_counts = orders_df["status"].value_counts()
        st.bar_chart(status_counts)
    else:
        st.info("No order data available")

    # =========================
    # RECENT ACTIVITY
    # =========================
    st.divider()
    st.subheader("🕒 Recent Activity")

    if not monitoring_df.empty:
        st.dataframe(monitoring_df.tail(5), use_container_width=True)
    else:
        st.info("No recent activity")