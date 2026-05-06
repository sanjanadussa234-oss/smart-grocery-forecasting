# ui/pages/manager_pages/home_dashboard.py
"""
Manager Home Dashboard
Shows store KPIs, recent orders summary, and quick-action buttons.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date

import sys
from pathlib import Path
# ui/ directory — works whether called from app.py or standalone
_UI_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_UI_DIR))
sys.path.insert(0, str(_UI_DIR / "pages"))

from utils.orders_db import get_order_stats_for_store, get_orders_for_store
from utils.api_client import check_api_health
from utils.config import STORE_NAMES


# ── status badge helper ───────────────────────────────────────────────────────
_STATUS_COLOR = {
    "pending":    "#F59E0B",
    "accepted":   "#3B82F6",
    "dispatched": "#8B5CF6",
    "delivered":  "#10B981",
    "cancelled":  "#EF4444",
}

def _badge(status: str) -> str:
    color = _STATUS_COLOR.get(status, "#6B7280")
    return (
        f'<span style="background:{color};color:white;padding:2px 10px;'
        f'border-radius:12px;font-size:0.78rem;font-weight:600;">'
        f'{status.upper()}</span>'
    )


# ── main page ─────────────────────────────────────────────────────────────────
def show():
    store_id    = st.session_state.store_id
    store_name  = STORE_NAMES.get(store_id, f"Store {store_id}")
    email       = st.session_state.user_email

    # ── header ────────────────────────────────────────────────────────────────
    col_title, col_api = st.columns([3, 1])
    with col_title:
        st.markdown(f"""
            <h2 style="color:#2E7D32;border-left:5px solid #2E7D32;padding-left:12px;margin-bottom:4px;">
                🏠 {store_name} Dashboard
            </h2>
            <p style="color:#6B7280;margin-left:17px;">
                Welcome back, <strong>{email}</strong> &nbsp;·&nbsp;
                {datetime.now().strftime("%A, %d %B %Y")}
            </p>
        """, unsafe_allow_html=True)

    with col_api:
        health = check_api_health()
        if health["status"] == "ok":
            st.success("🟢 API Online")
        else:
            st.error("🔴 API Offline")
            st.caption(health.get("message", ""))

    st.divider()

    # ── KPI metrics ───────────────────────────────────────────────────────────
    stats = get_order_stats_for_store(store_id)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("📦 Total Orders",   stats["total"])
    c2.metric("⏳ Pending",         stats["pending"])
    c3.metric("🚚 In Transit",      stats["active"])
    c4.metric("✅ Delivered",        stats["delivered"])
    c5.metric("💰 Total Value",     f"₹{stats['total_value']:,.0f}")

    st.divider()

    # ── quick actions ─────────────────────────────────────────────────────────
    st.markdown("#### ⚡ Quick Actions")
    qa1, qa2, qa3 = st.columns(3)

    with qa1:
        st.markdown("""
            <div style="background:linear-gradient(135deg,#E8F5E9,#C8E6C9);
                        border-radius:12px;padding:1.2rem;text-align:center;
                        border:1px solid #A5D6A7;">
                <div style="font-size:2rem;">📊</div>
                <strong>Single Prediction</strong>
                <p style="font-size:0.85rem;color:#555;margin-top:4px;">
                    Predict demand for one item
                </p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Go to Prediction →", key="qa_single", use_container_width=True):
            st.session_state["nav_override"] = "📊 Single Prediction"
            st.rerun()

    with qa2:
        st.markdown("""
            <div style="background:linear-gradient(135deg,#FFF3E0,#FFE0B2);
                        border-radius:12px;padding:1.2rem;text-align:center;
                        border:1px solid #FFCC80;">
                <div style="font-size:2rem;">🎉</div>
                <strong>Festival Forecast</strong>
                <p style="font-size:0.85rem;color:#555;margin-top:4px;">
                    Bulk predictions for festivals
                </p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Go to Festival →", key="qa_festival", use_container_width=True):
            st.session_state["nav_override"] = "🎉 Festival Prediction"
            st.rerun()

    with qa3:
        st.markdown("""
            <div style="background:linear-gradient(135deg,#E3F2FD,#BBDEFB);
                        border-radius:12px;padding:1.2rem;text-align:center;
                        border:1px solid #90CAF9;">
                <div style="font-size:2rem;">📦</div>
                <strong>Manage Orders</strong>
                <p style="font-size:0.85rem;color:#555;margin-top:4px;">
                    View and place orders
                </p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Go to Orders →", key="qa_orders", use_container_width=True):
            st.session_state["nav_override"] = "📦 Orders"
            st.rerun()

    st.divider()

    # ── recent orders table ───────────────────────────────────────────────────
    st.markdown("#### 🕒 Recent Orders (Last 5)")
    orders_df = get_orders_for_store(store_id)

    if orders_df.empty:
        st.info("No orders yet. Use **Single Prediction** or **Festival Forecast** to create your first order.")
    else:
        recent = orders_df.sort_values("created_at", ascending=False).head(5)
        # Build display table
        rows_html = ""
        for _, row in recent.iterrows():
            badge = _badge(str(row["status"]))
            rows_html += f"""
            <tr>
                <td style="padding:8px;font-weight:600;">#{row['order_id']}</td>
                <td style="padding:8px;">{row['item_name']}</td>
                <td style="padding:8px;">{row['category']}</td>
                <td style="padding:8px;text-align:right;">{float(row['quantity']):.0f} units</td>
                <td style="padding:8px;text-align:right;">₹{float(row['total_price']):,.0f}</td>
                <td style="padding:8px;">{badge}</td>
                <td style="padding:8px;color:#9CA3AF;font-size:0.8rem;">
                    {str(row['created_at'])[:10]}
                </td>
            </tr>
            """

        st.markdown(f"""
            <table style="width:100%;border-collapse:collapse;background:white;
                          border-radius:12px;overflow:hidden;
                          box-shadow:0 2px 8px rgba(0,0,0,0.08);">
                <thead>
                    <tr style="background:#F3F4F6;">
                        <th style="padding:10px;text-align:left;">Order ID</th>
                        <th style="padding:10px;text-align:left;">Item</th>
                        <th style="padding:10px;text-align:left;">Category</th>
                        <th style="padding:10px;text-align:right;">Qty</th>
                        <th style="padding:10px;text-align:right;">Value</th>
                        <th style="padding:10px;text-align:left;">Status</th>
                        <th style="padding:10px;text-align:left;">Date</th>
                    </tr>
                </thead>
                <tbody>{rows_html}</tbody>
            </table>
        """, unsafe_allow_html=True)