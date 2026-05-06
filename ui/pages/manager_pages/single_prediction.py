# ui/pages/manager_pages/single_prediction.py
"""
Single Item Prediction Page
Manager enters item details → calls /predict → sees demand → places order.
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta

import sys
from pathlib import Path
_UI_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_UI_DIR))
sys.path.insert(0, str(_UI_DIR / "pages"))

from utils.api_client import predict_single
from utils.orders_db  import create_order
from utils.config     import CATEGORIES, FESTIVALS, FESTIVAL_EMOJIS, STORE_NAMES


# ── constants ─────────────────────────────────────────────────────────────────
_SAFETY_STOCK_PCT = 0.15   # add 15 % buffer on top of predicted demand
_DEFAULT_UNIT_PRICE = 50.0


def _stock_recommendation(predicted: float) -> dict:
    """Calculate order quantity and stock recommendations."""
    buffer       = predicted * _SAFETY_STOCK_PCT
    order_qty    = round(predicted + buffer)
    reorder_pt   = round(predicted * 0.25)
    return {
        "predicted":   round(predicted, 1),
        "buffer":      round(buffer, 1),
        "order_qty":   order_qty,
        "reorder_pt":  reorder_pt,
    }


# ── main page ─────────────────────────────────────────────────────────────────
def show():
    store_id   = st.session_state.store_id
    store_name = STORE_NAMES.get(store_id, f"Store {store_id}")

    st.markdown(f"""
        <h2 style="color:#2E7D32;border-left:5px solid #2E7D32;padding-left:12px;">
            📊 Single Item Prediction — {store_name}
        </h2>
        <p style="color:#6B7280;margin-left:17px;">
            Predict demand for one item and optionally place a stock order.
        </p>
    """, unsafe_allow_html=True)

    st.divider()

    # ── input form ────────────────────────────────────────────────────────────
    with st.form("single_prediction_form", clear_on_submit=False):
        st.markdown("#### 📝 Item Details")

        col1, col2 = st.columns(2)
        with col1:
            item_name = st.text_input(
                "Item Name *",
                placeholder="e.g. Basmati Rice",
                help="Name of the grocery item",
            )
            category = st.selectbox("Category *", CATEGORIES)
            prediction_date = st.date_input(
                "Prediction Date *",
                value=date.today() + timedelta(days=1),
                min_value=date.today(),
                help="Date you want demand for",
            )

        with col2:
            festival_options = [f"{FESTIVAL_EMOJIS[f]} {f.title()}" for f in FESTIVALS]
            festival_display = st.selectbox(
                "Festival / Occasion",
                festival_options,
                index=FESTIVALS.index("none"),
            )
            # strip emoji back to raw festival key
            festival = FESTIVALS[festival_options.index(festival_display)]

            current_stock = st.number_input(
                "Current Stock (units)",
                min_value=0.0,
                max_value=100000.0,
                value=0.0,
                step=1.0,
                help="Current stock level for this item",
            )
            discount_pct = st.slider(
                "Discount (%)",
                min_value=0,
                max_value=50,
                value=0,
                help="Promotional discount percentage",
            )
            has_promotion = st.checkbox("Has Promotion?", value=False)

        st.divider()
        submitted = st.form_submit_button(
            "🔮 Predict Demand",
            use_container_width=True,
            type="primary",
        )

    # ── prediction result ─────────────────────────────────────────────────────
    if submitted:
        if not item_name.strip():
            st.error("❌ Please enter an item name")
            return

        with st.spinner("🤖 Calling prediction model..."):
            result = predict_single(
                store_id      = store_id,
                item_name     = item_name.strip(),
                category      = category,
                current_stock = float(current_stock),
                festival      = festival,
                has_discount  = discount_pct > 0,
                discount_pct  = float(discount_pct),
                has_promotion = has_promotion,
                promotion     = int(has_promotion),
            )

        if not result.get("success"):
            st.error(f"❌ Prediction failed: {result.get('error', 'Unknown error')}")
            st.info("💡 Make sure the FastAPI server is running on http://localhost:8000")
            return

        # ── store result in session for the order form below ──────────────
        st.session_state["last_prediction"] = {
            "item_name":        item_name.strip(),
            "category":         category,
            "festival":         festival,
            "prediction_date":  prediction_date.isoformat(),
            "predicted_demand": result.get("predicted_demand", 0),
            "base_price":       _DEFAULT_UNIT_PRICE,
        }

    # ── show results if available ─────────────────────────────────────────────
    if "last_prediction" not in st.session_state:
        return

    pred = st.session_state["last_prediction"]
    rec  = _stock_recommendation(pred["predicted_demand"])

    st.divider()
    st.markdown("### 🎯 Prediction Results")

    # headline metric
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("🔮 Predicted Demand", f"{rec['predicted']} units")
    col_m2.metric("📦 Recommended Order", f"{rec['order_qty']} units",
                  help=f"Includes {_SAFETY_STOCK_PCT*100:.0f}% safety stock buffer")
    col_m3.metric("⚠️ Reorder Point", f"{rec['reorder_pt']} units",
                  help="Reorder when stock hits this level")
    col_m4.metric("💰 Estimated Value",
                  f"₹{rec['order_qty'] * pred['base_price']:,.0f}")

    # detail card
    st.markdown(f"""
        <div style="background:linear-gradient(135deg,#E8F5E9,#F1F8E9);
                    border-radius:12px;padding:1.2rem 1.5rem;
                    border:1px solid #A5D6A7;margin-top:1rem;">
            <table style="width:100%;border-collapse:collapse;">
                <tr>
                    <td style="padding:4px 12px;color:#555;">🛍️ Item</td>
                    <td style="padding:4px 12px;font-weight:600;">{pred['item_name']}</td>
                    <td style="padding:4px 12px;color:#555;">📂 Category</td>
                    <td style="padding:4px 12px;font-weight:600;">{pred['category']}</td>
                </tr>
                <tr>
                    <td style="padding:4px 12px;color:#555;">📅 Date</td>
                    <td style="padding:4px 12px;font-weight:600;">{pred['prediction_date']}</td>
                    <td style="padding:4px 12px;color:#555;">🎊 Festival</td>
                    <td style="padding:4px 12px;font-weight:600;">{pred['festival'].title()}</td>
                </tr>
                <tr>
                    <td style="padding:4px 12px;color:#555;">💵 Unit Price</td>
                    <td style="padding:4px 12px;font-weight:600;">₹{pred['base_price']:.2f}</td>
                    <td style="padding:4px 12px;color:#555;">📦 Safety Buffer</td>
                    <td style="padding:4px 12px;font-weight:600;">{rec['buffer']} units</td>
                </tr>
            </table>
        </div>
    """, unsafe_allow_html=True)

    # ── save to history ───────────────────────────────────────────────────────
    if "predictions_history" not in st.session_state:
        st.session_state.predictions_history = []

    # avoid duplicate appends on re-render
    history_ids = [p.get("_ts") for p in st.session_state.predictions_history]
    ts_key = f"{pred['item_name']}_{pred['prediction_date']}"
    if ts_key not in history_ids:
        entry = {**pred, "_ts": ts_key, "rec_qty": rec["order_qty"]}
        st.session_state.predictions_history.insert(0, entry)
        st.session_state.predictions_history = st.session_state.predictions_history[:50]

    st.divider()

    # ── place order form ───────────────────────────────────────────────────────
    st.markdown("### 📦 Place Stock Order")
    st.caption("Review and confirm the order quantity before placing.")

    with st.form("place_order_form"):
        oc1, oc2 = st.columns(2)
        with oc1:
            order_qty = st.number_input(
                "Order Quantity (units)",
                min_value=1,
                value=int(rec["order_qty"]),
                step=1,
                help="You can adjust the recommended quantity",
            )
        with oc2:
            unit_price = st.number_input(
                "Unit Price (₹)",
                min_value=1.0,
                value=float(pred["base_price"]),
                step=1.0,
            )

        order_notes = st.text_area(
            "Notes (optional)",
            placeholder="Any special instructions for the supplier...",
            height=80,
        )

        place_btn = st.form_submit_button(
            "✅ Place Order",
            use_container_width=True,
            type="primary",
        )

    if place_btn:
        result = create_order(
            store_id        = store_id,
            manager_email   = st.session_state.user_email,
            item_name       = pred["item_name"],
            category        = pred["category"],
            quantity        = order_qty,
            unit_price      = unit_price,
            festival        = pred["festival"],
            prediction_date = pred["prediction_date"],
            notes           = order_notes,
        )
        if result["success"]:
            st.success(f"✅ Order **#{result['order_id']}** placed successfully!")
            st.balloons()
            # clear last prediction so form resets cleanly
            del st.session_state["last_prediction"]
        else:
            st.error(f"❌ Failed to place order: {result.get('error')}")

    # ── prediction history ────────────────────────────────────────────────────
    if st.session_state.get("predictions_history"):
        with st.expander("🕒 Recent Predictions (this session)", expanded=False):
            hist_df = pd.DataFrame(st.session_state.predictions_history)
            display_cols = ["item_name", "category", "prediction_date",
                            "festival", "predicted_demand", "rec_qty"]
            display_cols = [c for c in display_cols if c in hist_df.columns]
            st.dataframe(hist_df[display_cols], use_container_width=True, hide_index=True)