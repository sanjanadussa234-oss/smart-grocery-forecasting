# ui/pages/manager_pages/festival_prediction.py
"""
Festival Prediction Page
Manager selects a festival → calls /predict/festival → bulk predictions
→ select items → place bulk orders.
"""

import streamlit as st
import pandas as pd
from datetime import date

import sys
from pathlib import Path
_UI_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_UI_DIR))
sys.path.insert(0, str(_UI_DIR / "pages"))

from utils.api_client import predict_festival
from utils.orders_db  import create_order
from utils.config     import CATEGORIES, FESTIVALS, FESTIVAL_EMOJIS, STORE_NAMES

_SAFETY_STOCK_PCT = 0.20   # 20 % buffer for festival orders (higher uncertainty)


def show():
    store_id   = st.session_state.store_id
    store_name = STORE_NAMES.get(store_id, f"Store {store_id}")

    st.markdown(f"""
        <h2 style="color:#2E7D32;border-left:5px solid #2E7D32;padding-left:12px;">
            🎉 Festival Demand Forecast — {store_name}
        </h2>
        <p style="color:#6B7280;margin-left:17px;">
            Get bulk demand predictions for all items during a festival period.
        </p>
    """, unsafe_allow_html=True)

    st.divider()

    # ── festival selector ─────────────────────────────────────────────────────
    festivals_no_none = [f for f in FESTIVALS if f != "none"]
    emoji_options     = [f"{FESTIVAL_EMOJIS[f]} {f.title()}" for f in festivals_no_none]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        festival_display = st.selectbox(
            "🎊 Select Festival",
            emoji_options,
            help="Choose the upcoming festival",
        )
        festival = festivals_no_none[emoji_options.index(festival_display)]

    with col2:
        top_n = st.number_input(
            "🔢 Top N Items",
            min_value=1,
            max_value=50,
            value=5,
            help="Number of top items to predict",
        )

    with col3:
        discount_pct = st.slider(
            "Discount (%)",
            min_value=0,
            max_value=50,
            value=0,
        )

    with col4:
        has_promotion = st.checkbox("Has Promotion?", value=False)

    st.divider()

    # ── call API ───────────────────────────────────────────────────────────────
    if st.button("🔮 Generate Festival Forecast", type="primary", use_container_width=False):
        with st.spinner(f"🤖 Generating predictions for {festival_display}..."):
            result = predict_festival(
                store_id      = store_id,
                festival      = festival,
                top_n         = int(top_n),
                has_discount  = discount_pct > 0,
                discount_pct  = float(discount_pct),
                has_promotion = has_promotion,
                promotion     = int(has_promotion),
            )

        if not result.get("success"):
            st.error(f"❌ Prediction failed: {result.get('error', 'Unknown error')}")
            st.info("💡 Make sure the FastAPI server is running on http://localhost:8000")
            return

        # FastAPI returns a list directly
        predictions = result if isinstance(result, list) else result.get("predictions", [])
        if not predictions:
            st.warning("⚠️ No predictions returned. Check your model/API logs.")
            return

        # store in session
        st.session_state["festival_predictions"] = {
            "festival":    festival,
            "date":        date.today().isoformat(),
            "predictions": predictions,
        }

    # ── show results ───────────────────────────────────────────────────────────
    if "festival_predictions" not in st.session_state:
        # show info card if nothing run yet
        st.markdown("""
            <div style="background:#F9FAFB;border:1px dashed #D1D5DB;
                        border-radius:12px;padding:2rem;text-align:center;color:#6B7280;">
                <div style="font-size:3rem;">🎊</div>
                <p style="font-size:1.1rem;">Select a festival and click <strong>Generate Festival Forecast</strong></p>
            </div>
        """, unsafe_allow_html=True)
        return

    fp        = st.session_state["festival_predictions"]
    pred_list = fp["predictions"]
    df        = pd.DataFrame(pred_list)

    # add recommended order qty
    df["order_qty"] = (df["predicted_demand"] * (1 + _SAFETY_STOCK_PCT)).round().astype(int)

    # ── summary metrics ────────────────────────────────────────────────────────
    st.markdown(f"""
        <div style="background:linear-gradient(135deg,#FFF8E1,#FFF3E0);
                    border-radius:12px;padding:1rem 1.5rem;border:1px solid #FFE082;
                    margin-bottom:1rem;">
            <strong>🎊 {fp['festival'].title()} Forecast</strong>
            &nbsp;·&nbsp; 📅 {fp['date']}
            &nbsp;·&nbsp; 🏪 {store_name}
            &nbsp;·&nbsp; 📋 {len(df)} items predicted
        </div>
    """, unsafe_allow_html=True)

    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric("📋 Items",           len(df))
    mc2.metric("📈 Total Demand",    f"{df['predicted_demand'].sum():,.0f} units")
    mc3.metric("📦 Total Order Qty", f"{df['order_qty'].sum():,.0f} units")
    mc4.metric("📂 Categories",      df["category"].nunique() if "category" in df.columns else "—")

    st.divider()

    # ── results table with selection ──────────────────────────────────────────
    st.markdown("#### 📋 Prediction Results — Select items to order")

    # filter by category
    categories_in_result = sorted(df["category"].unique()) if "category" in df.columns else []
    if categories_in_result:
        cat_filter = st.multiselect(
            "Filter by Category",
            categories_in_result,
            default=categories_in_result,
            key="fest_cat_filter",
        )
        view_df = df[df["category"].isin(cat_filter)].copy()
    else:
        view_df = df.copy()

    # build editable table
    view_df["select"]     = True
    view_df["unit_price"] = 50.0    # default; manager can edit

    edited = st.data_editor(
        view_df[["select", "item_name", "category",
                 "predicted_demand", "order_qty", "unit_price"]],
        column_config={
            "select":           st.column_config.CheckboxColumn("Order?", default=True),
            "item_name":        st.column_config.TextColumn("Item", disabled=True),
            "category":         st.column_config.TextColumn("Category", disabled=True),
            "predicted_demand": st.column_config.NumberColumn("Pred. Demand", disabled=True, format="%.1f"),
            "order_qty":        st.column_config.NumberColumn("Order Qty", min_value=1),
            "unit_price":       st.column_config.NumberColumn("Unit Price (₹)", min_value=1.0, format="₹%.2f"),
        },
        use_container_width=True,
        hide_index=True,
        key="festival_editor",
    )

    selected_rows = edited[edited["select"] == True]
    total_value   = (selected_rows["order_qty"] * selected_rows["unit_price"]).sum()

    st.markdown(f"""
        <div style="background:#F0FDF4;border-radius:8px;padding:0.75rem 1rem;
                    border:1px solid #BBF7D0;margin-top:0.5rem;">
            ✅ <strong>{len(selected_rows)}</strong> items selected
            &nbsp;·&nbsp;
            📦 <strong>{int(selected_rows['order_qty'].sum()):,}</strong> total units
            &nbsp;·&nbsp;
            💰 Estimated value: <strong>₹{total_value:,.0f}</strong>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── bulk place orders ──────────────────────────────────────────────────────
    st.markdown("#### 📦 Place Bulk Orders")

    bulk_notes = st.text_area(
        "Notes for all orders (optional)",
        placeholder=f"e.g. Festival: {fp['festival'].title()} stock replenishment",
        value=f"Festival order: {fp['festival'].title()} — {fp['date']}",
        height=70,
        key="bulk_notes",
    )

    if st.button(
        f"✅ Place {len(selected_rows)} Orders",
        type="primary",
        disabled=len(selected_rows) == 0,
    ):
        if selected_rows.empty:
            st.warning("⚠️ No items selected")
            return

        placed, failed = 0, 0
        progress = st.progress(0, text="Placing orders...")

        for i, (_, row) in enumerate(selected_rows.iterrows()):
            res = create_order(
                store_id        = store_id,
                manager_email   = st.session_state.user_email,
                item_name       = str(row["item_name"]),
                category        = str(row["category"]),
                quantity        = int(row["order_qty"]),
                unit_price      = float(row["unit_price"]),
                festival        = fp["festival"],
                prediction_date = fp["date"],
                notes           = bulk_notes,
            )
            if res["success"]:
                placed += 1
            else:
                failed += 1
            progress.progress((i + 1) / len(selected_rows),
                               text=f"Placed {placed} / {len(selected_rows)}...")

        progress.empty()

        if failed == 0:
            st.success(f"🎉 All {placed} orders placed successfully!")
            st.balloons()
            del st.session_state["festival_predictions"]
        else:
            st.warning(f"⚠️ {placed} orders placed, {failed} failed.")