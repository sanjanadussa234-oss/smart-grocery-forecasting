# ui/pages/admin_pages/mlops_dashboard.py

import streamlit as st
import pandas as pd
from pathlib import Path

# path to monitoring file
MONITORING_FILE = Path(__file__).parent.parent.parent / "data" / "monitoring.csv"


def load_monitoring_data():
    if not MONITORING_FILE.exists():
        return pd.DataFrame()

    try:
        df = pd.read_csv(MONITORING_FILE)
        return df
    except:
        return pd.DataFrame()


def show():
    st.title("📊 MLOps Monitoring Dashboard")

    df = load_monitoring_data()

    if df.empty:
        st.warning("⚠️ No monitoring data available yet.")
        st.info("Run predictions + pipeline to generate monitoring logs.")
        return

    # =========================
    # LATEST STATUS
    # =========================
    latest = df.iloc[-1]

    st.subheader("🔍 Latest System Status")

    col1, col2, col3 = st.columns(3)

    with col1:
        drift = "YES" if latest.get("drift_detected", False) else "NO"
        st.metric("Drift Detected", drift)

    with col2:
        st.metric("RMSE", round(latest.get("rmse", 0), 2))

    with col3:
        st.metric("MAE", round(latest.get("mae", 0), 2))

    st.divider()

    # =========================
    # RETRAINING STATUS
    # =========================
    st.subheader("🔁 Retraining Status")

    col1, col2 = st.columns(2)

    with col1:
        retrained = "YES" if latest.get("retrained", False) else "NO"
        st.metric("Retraining Triggered", retrained)

    with col2:
        st.metric("Last Timestamp", latest.get("timestamp", "N/A"))

    # =========================
    # ALERTS
    # =========================
    st.divider()
    st.subheader("🚨 Alerts")

    if latest.get("drift_detected", False):
        st.error("🚨 Data Drift Detected! Model may need retraining.")

    if latest.get("retrained", False):
        st.success("✅ Model Retrained Successfully!")

    if not latest.get("drift_detected", False) and not latest.get("retrained", False):
        st.info("✅ System Stable — No issues detected")

    # =========================
    # TREND GRAPH
    # =========================
    st.divider()
    st.subheader("📈 Performance Trends")

    if "rmse" in df.columns:
        st.line_chart(df["rmse"])

    if "mae" in df.columns:
        st.line_chart(df["mae"])

    # =========================
    # FULL TABLE
    # =========================
    st.divider()
    st.subheader("📄 Monitoring Logs")

    st.dataframe(df, use_container_width=True)