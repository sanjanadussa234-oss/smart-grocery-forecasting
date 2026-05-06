# ui/pages/manager_pages/orders_page.py
"""
Manager Orders Page
View all orders for this store, filter by status, cancel pending orders.
"""

import streamlit as st
import pandas as pd

import sys
from pathlib import Path
_UI_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_UI_DIR))
sys.path.insert(0, str(_UI_DIR / "pages"))

from utils.orders_db import (
    get_orders_for_store,
    get_order_stats_for_store,
    cancel_order,
)
from utils.config import STORE_NAMES

_STATUS_COLOR = {
    "pending":    "#F59E0B",
    "accepted":   "#3B82F6",
    "dispatched": "#8B5CF6",
    "delivered":  "#10B981",
    "cancelled":  "#EF4444",
}
_STATUS_BG = {
    "pending":    "#FEF3C7",
    "accepted":   "#DBEAFE",
    "dispatched": "#EDE9FE",
    "delivered":  "#D1FAE5",
    "cancelled":  "#FEE2E2",
}

def _badge(status: str) -> str:
    color = _STATUS_COLOR.get(status, "#6B7280")
    return (
        f'<span style="background:{color};color:white;padding:3px 10px;'
        f'border-radius:12px;font-size:0.78rem;font-weight:600;">'
        f'{status.upper()}</span>'
    )


def show():
    store_id   = st.session_state.store_id
    store_name = STORE_NAMES.get(store_id, f"Store {store_id}")

    st.markdown(f"""
        <h2 style="color:#2E7D32;border-left:5px solid #2E7D32;padding-left:12px;">
            📦 Orders — {store_name}
        </h2>
        <p style="color:#6B7280;margin-left:17px;">
            Track all your stock orders and their current status.
        </p>
    """, unsafe_allow_html=True)

    st.divider()

    # ── KPI row ────────────────────────────────────────────────────────────────
    stats = get_order_stats_for_store(store_id)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("📦 Total",      stats["total"])
    c2.metric("⏳ Pending",     stats["pending"])
    c3.metric("🚚 In Transit",  stats["active"])
    c4.metric("✅ Delivered",    stats["delivered"])
    c5.metric("💰 Total Value", f"₹{stats['total_value']:,.0f}")

    st.divider()

    # ── load orders ────────────────────────────────────────────────────────────
    orders_df = get_orders_for_store(store_id)

    if orders_df.empty:
        st.info("📭 No orders yet. Go to **Single Prediction** or **Festival Forecast** to place your first order.")
        return

    # ── filters ────────────────────────────────────────────────────────────────
    col_f1, col_f2, col_f3 = st.columns([2, 2, 2])
    with col_f1:
        all_statuses = ["All"] + sorted(orders_df["status"].unique().tolist())
        status_filter = st.selectbox("Filter by Status", all_statuses)
    with col_f2:
        all_cats = ["All"] + sorted(orders_df["category"].unique().tolist())
        cat_filter = st.selectbox("Filter by Category", all_cats)
    with col_f3:
        search = st.text_input("🔍 Search Item Name", placeholder="e.g. Rice")

    # apply filters
    filtered = orders_df.copy()
    if status_filter != "All":
        filtered = filtered[filtered["status"] == status_filter]
    if cat_filter != "All":
        filtered = filtered[filtered["category"] == cat_filter]
    if search:
        filtered = filtered[
            filtered["item_name"].str.contains(search, case=False, na=False)
        ]

    st.markdown(f"**{len(filtered)}** orders found")
    st.divider()

    if filtered.empty:
        st.warning("No orders match the current filters.")
        return

    # ── orders list ────────────────────────────────────────────────────────────
    filtered_sorted = filtered.sort_values("created_at", ascending=False)

    for _, row in filtered_sorted.iterrows():
        status      = str(row["status"])
        bg_color    = _STATUS_BG.get(status, "#F9FAFB")
        border_col  = _STATUS_COLOR.get(status, "#E5E7EB")

        with st.container():
            st.markdown(f"""
                <div style="background:{bg_color};border-left:4px solid {border_col};
                            border-radius:8px;padding:1rem 1.2rem;margin-bottom:0.5rem;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="font-weight:700;font-size:1rem;">
                            #{row['order_id']} &nbsp;·&nbsp; {row['item_name']}
                        </span>
                        {_badge(status)}
                    </div>
                    <div style="margin-top:0.5rem;font-size:0.88rem;color:#374151;">
                        📂 {row['category']}
                        &nbsp;|&nbsp;
                        📦 {float(row['quantity']):.0f} units
                        &nbsp;|&nbsp;
                        💰 ₹{float(row['total_price']):,.0f}
                        &nbsp;|&nbsp;
                        📅 {str(row['created_at'])[:10]}
                        &nbsp;|&nbsp;
                        🎊 {str(row['festival']).title()}
                    </div>
                    {"<div style='margin-top:4px;font-size:0.82rem;color:#6B7280;'>📝 " + str(row['notes']) + "</div>" if row.get('notes') else ""}
                </div>
            """, unsafe_allow_html=True)

            # cancel button — only for pending orders
            if status == "pending":
                btn_col, _ = st.columns([1, 5])
                with btn_col:
                    if st.button(
                        "❌ Cancel",
                        key=f"cancel_{row['order_id']}",
                        help="Cancel this pending order",
                    ):
                        res = cancel_order(
                            row["order_id"],
                            reason="Cancelled by manager",
                        )
                        if res["success"]:
                            st.success(f"Order #{row['order_id']} cancelled.")
                            st.rerun()
                        else:
                            st.error(res.get("error", "Cancel failed"))

    # ── export ─────────────────────────────────────────────────────────────────
    st.divider()
    st.markdown("#### 📥 Export Orders")
    csv_data = filtered_sorted.to_csv(index=False)
    st.download_button(
        label="⬇️ Download as CSV",
        data=csv_data,
        file_name=f"orders_store{store_id}.csv",
        mime="text/csv",
    )