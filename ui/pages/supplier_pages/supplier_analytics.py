# ui/pages/supplier_pages/supplier_analytics.py
"""
Supplier Analytics Page
Business overview: orders by store, category, status, value trends.
Uses only orders.csv — no external API calls needed.
"""

import streamlit as st
import pandas as pd

import sys
from pathlib import Path
_UI_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_UI_DIR))
sys.path.insert(0, str(_UI_DIR / "pages"))

from utils.orders_db import get_all_orders
from utils.config    import STORE_NAMES


def show():
    st.markdown("""
        <h2 style="color:#2E7D32;border-left:5px solid #2E7D32;padding-left:12px;">
            📊 Supplier Analytics
        </h2>
        <p style="color:#6B7280;margin-left:17px;">
            Business overview across all stores and categories.
        </p>
    """, unsafe_allow_html=True)

    st.divider()

    df = get_all_orders()

    if df.empty:
        st.info("📭 No order data yet. Orders will appear here once managers place them.")
        return

    # ── ensure correct dtypes ──────────────────────────────────────────────────
    df["total_price"] = pd.to_numeric(df["total_price"], errors="coerce").fillna(0)
    df["quantity"]    = pd.to_numeric(df["quantity"],    errors="coerce").fillna(0)
    df["store_id"]    = pd.to_numeric(df["store_id"],    errors="coerce").fillna(0).astype(int)
    df["created_at"]  = pd.to_datetime(df["created_at"], errors="coerce")
    df["store_label"] = df["store_id"].map(lambda x: STORE_NAMES.get(x, f"Store {x}"))

    # ── top KPIs ───────────────────────────────────────────────────────────────
    total_orders   = len(df)
    total_value    = df["total_value"] if "total_value" in df.columns else df["total_price"].sum()
    total_revenue  = df["total_price"].sum()
    delivered_pct  = (df["status"] == "delivered").sum() / max(total_orders, 1) * 100
    pending_count  = (df["status"] == "pending").sum()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("📦 Total Orders",    f"{total_orders:,}")
    k2.metric("💰 Total Value",     f"₹{total_revenue:,.0f}")
    k3.metric("✅ Delivery Rate",   f"{delivered_pct:.1f}%")
    k4.metric("⏳ Pending Orders",  f"{pending_count}")

    st.divider()

    # ── charts row 1 ──────────────────────────────────────────────────────────
    col_a, col_b = st.columns(2)

    # orders by store
    with col_a:
        st.markdown("##### 🏪 Orders by Store")
        store_counts = (
            df.groupby("store_label")
              .agg(orders=("order_id", "count"), value=("total_price", "sum"))
              .reset_index()
              .sort_values("orders", ascending=False)
        )
        st.bar_chart(store_counts.set_index("store_label")["orders"])

    # orders by category
    with col_b:
        st.markdown("##### 📂 Orders by Category")
        cat_counts = (
            df.groupby("category")
              .agg(orders=("order_id", "count"), value=("total_price", "sum"))
              .reset_index()
              .sort_values("orders", ascending=False)
        )
        st.bar_chart(cat_counts.set_index("category")["orders"])

    st.divider()

    # ── charts row 2 ──────────────────────────────────────────────────────────
    col_c, col_d = st.columns(2)

    # status distribution
    with col_c:
        st.markdown("##### 🔄 Order Status Distribution")
        status_counts = df["status"].value_counts().reset_index()
        status_counts.columns = ["status", "count"]
        st.bar_chart(status_counts.set_index("status")["count"])

    # revenue by store
    with col_d:
        st.markdown("##### 💰 Revenue by Store")
        revenue_df = (
            df.groupby("store_label")["total_price"]
              .sum()
              .reset_index()
              .rename(columns={"total_price": "revenue"})
              .sort_values("revenue", ascending=False)
        )
        st.bar_chart(revenue_df.set_index("store_label")["revenue"])

    st.divider()

    # ── daily order trend (if date data is available) ─────────────────────────
    if df["created_at"].notna().any():
        st.markdown("##### 📅 Daily Orders Trend")
        daily = (
            df.dropna(subset=["created_at"])
              .groupby(df["created_at"].dt.date)
              .agg(orders=("order_id","count"), value=("total_price","sum"))
              .reset_index()
              .rename(columns={"created_at": "date"})
        )
        if len(daily) > 1:
            st.line_chart(daily.set_index("date")["orders"])
        else:
            st.info("Not enough data for trend chart (need at least 2 days of orders).")

        st.divider()

    # ── top items table ────────────────────────────────────────────────────────
    st.markdown("##### 🏆 Top Ordered Items")
    top_items = (
        df.groupby(["item_name", "category"])
          .agg(
              total_orders   = ("order_id",    "count"),
              total_quantity = ("quantity",    "sum"),
              total_value    = ("total_price", "sum"),
          )
          .reset_index()
          .sort_values("total_orders", ascending=False)
          .head(15)
    )
    top_items["total_value"] = top_items["total_value"].map("₹{:,.0f}".format)
    top_items["total_quantity"] = top_items["total_quantity"].map("{:,.0f}".format)
    st.dataframe(top_items, use_container_width=True, hide_index=True)

    st.divider()

    # ── store breakdown table ──────────────────────────────────────────────────
    st.markdown("##### 📋 Store-wise Summary")
    store_summary = (
        df.groupby("store_label")
          .agg(
              total_orders  = ("order_id",    "count"),
              pending       = ("status",      lambda x: (x == "pending").sum()),
              delivered     = ("status",      lambda x: (x == "delivered").sum()),
              total_value   = ("total_price", "sum"),
          )
          .reset_index()
          .rename(columns={"store_label": "Store"})
    )
    store_summary["total_value"] = store_summary["total_value"].map("₹{:,.0f}".format)
    st.dataframe(store_summary, use_container_width=True, hide_index=True)

    # export
    st.divider()
    st.download_button(
        "⬇️ Export All Orders CSV",
        data=df.to_csv(index=False),
        file_name="all_orders_export.csv",
        mime="text/csv",
    )