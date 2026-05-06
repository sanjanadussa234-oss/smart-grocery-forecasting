# ui/pages/supplier_pages/supplier_orders.py
"""
Supplier Orders Page
Shows active + completed orders across ALL stores.
Supplier can accept, dispatch, and mark orders as delivered.
"""

import streamlit as st
import pandas as pd

import sys
from pathlib import Path
_UI_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_UI_DIR))
sys.path.insert(0, str(_UI_DIR / "pages"))

from utils.orders_db import (
    get_active_orders,
    get_completed_orders,
    get_global_order_stats,
    update_order_status,
)
from utils.config import STORE_NAMES

_STATUS_COLOR = {
    "pending":    "#F59E0B",
    "accepted":   "#3B82F6",
    "dispatched": "#8B5CF6",
    "delivered":  "#10B981",
    "cancelled":  "#EF4444",
}

# valid supplier transitions
_NEXT_STATUS = {
    "pending":    ("accepted",   "✅ Accept"),
    "accepted":   ("dispatched", "🚚 Mark Dispatched"),
    "dispatched": ("delivered",  "📬 Mark Delivered"),
}

def _badge(status: str) -> str:
    color = _STATUS_COLOR.get(status, "#6B7280")
    return (
        f'<span style="background:{color};color:white;padding:3px 10px;'
        f'border-radius:12px;font-size:0.78rem;font-weight:600;">'
        f'{status.upper()}</span>'
    )


def _render_order_card(row: pd.Series, show_action: bool = True):
    """Render a single order card."""
    status      = str(row["status"])
    store_label = STORE_NAMES.get(int(row["store_id"]), f"Store {row['store_id']}")
    border_col  = _STATUS_COLOR.get(status, "#E5E7EB")

    st.markdown(f"""
        <div style="background:white;border-left:4px solid {border_col};
                    border-radius:8px;padding:1rem 1.2rem;margin-bottom:0.4rem;
                    box-shadow:0 1px 4px rgba(0,0,0,0.06);">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="font-weight:700;font-size:1rem;">
                    #{row['order_id']} &nbsp;·&nbsp; {row['item_name']}
                </span>
                {_badge(status)}
            </div>
            <div style="margin-top:0.5rem;font-size:0.88rem;color:#374151;">
                🏪 {store_label}
                &nbsp;|&nbsp;
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

    if show_action and status in _NEXT_STATUS:
        next_status, btn_label = _NEXT_STATUS[status]
        btn_col, note_col, _ = st.columns([1, 2, 3])
        with btn_col:
            if st.button(btn_label, key=f"action_{row['order_id']}"):
                res = update_order_status(row["order_id"], next_status)
                if res["success"]:
                    st.success(f"Order #{row['order_id']} → {next_status}")
                    st.rerun()
                else:
                    st.error(res.get("error"))


def show():
    st.markdown("""
        <h2 style="color:#2E7D32;border-left:5px solid #2E7D32;padding-left:12px;">
            📤 Orders Management
        </h2>
        <p style="color:#6B7280;margin-left:17px;">
            View and manage orders from all stores.
        </p>
    """, unsafe_allow_html=True)

    st.divider()

    # ── global KPIs ────────────────────────────────────────────────────────────
    stats = get_global_order_stats()
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("📦 Total Orders",  stats["total"])
    c2.metric("⏳ Pending",        stats["pending"])
    c3.metric("🚚 Active",         stats["active"])
    c4.metric("✅ Delivered",       stats["delivered"])
    c5.metric("💰 Total Value",    f"₹{stats['total_value']:,.0f}")

    st.divider()

    # ── tabs: Active / Completed ───────────────────────────────────────────────
    tab_active, tab_done = st.tabs(["🚀 Active Orders", "✅ Completed Orders"])

    # ── ACTIVE TAB ─────────────────────────────────────────────────────────────
    with tab_active:
        active_df = get_active_orders()

        if active_df.empty:
            st.info("🎉 No active orders right now.")
        else:
            # store filter
            store_opts = ["All Stores"] + [
                STORE_NAMES.get(int(s), f"Store {s}")
                for s in sorted(active_df["store_id"].unique())
            ]
            store_filter = st.selectbox(
                "Filter by Store", store_opts, key="active_store_filter"
            )

            view = active_df.copy()
            if store_filter != "All Stores":
                store_id_map = {v: k for k, v in STORE_NAMES.items()}
                sid = store_id_map.get(store_filter)
                if sid is not None:
                    view = view[view["store_id"] == sid]

            # group by status for clarity
            for status_label in ["pending", "accepted", "dispatched"]:
                subset = view[view["status"] == status_label]
                if subset.empty:
                    continue
                badge_html = _badge(status_label)
                st.markdown(
                    f"##### {badge_html} &nbsp; {len(subset)} order(s)",
                    unsafe_allow_html=True,
                )
                for _, row in subset.sort_values("created_at").iterrows():
                    _render_order_card(row, show_action=True)
                st.markdown("")

    # ── COMPLETED TAB ──────────────────────────────────────────────────────────
    with tab_done:
        done_df = get_completed_orders()

        if done_df.empty:
            st.info("No completed orders yet.")
        else:
            # filters
            f1, f2 = st.columns(2)
            with f1:
                store_opts2 = ["All Stores"] + [
                    STORE_NAMES.get(int(s), f"Store {s}")
                    for s in sorted(done_df["store_id"].unique())
                ]
                store_filter2 = st.selectbox(
                    "Filter by Store", store_opts2, key="done_store_filter"
                )
            with f2:
                status_opts = ["All", "delivered", "cancelled"]
                status_filter2 = st.selectbox(
                    "Filter by Status", status_opts, key="done_status_filter"
                )

            view2 = done_df.copy()
            if store_filter2 != "All Stores":
                store_id_map2 = {v: k for k, v in STORE_NAMES.items()}
                sid2 = store_id_map2.get(store_filter2)
                if sid2 is not None:
                    view2 = view2[view2["store_id"] == sid2]
            if status_filter2 != "All":
                view2 = view2[view2["status"] == status_filter2]

            st.markdown(f"**{len(view2)}** completed orders")

            for _, row in view2.sort_values("updated_at", ascending=False).iterrows():
                _render_order_card(row, show_action=False)

            # export
            st.divider()
            csv = view2.to_csv(index=False)
            st.download_button(
                "⬇️ Download Completed Orders CSV",
                data=csv,
                file_name="completed_orders.csv",
                mime="text/csv",
            )