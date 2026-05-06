# ui/app.py
"""
Smart Grocery Demand Forecasting System
Main Streamlit Application — Phase 2
Role-based routing: Manager | Supplier | Admin
"""

import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from utils.auth   import init_session_state, show_auth_page
from utils.config import APP_TITLE, APP_ICON, STORE_NAMES

# ── page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title = APP_TITLE,
    page_icon  = APP_ICON,
    layout     = "wide",
    initial_sidebar_state = "expanded",
)

# ── global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap');
* { font-family: 'Poppins', sans-serif !important; }
body, .stApp { background: linear-gradient(135deg, #FAFAFA 0%, #F3F4F6 100%); }
h1,h2,h3,h4,h5,h6 { color:#000 !important; font-weight:700; }
h2 { border-left:4px solid #2E7D32; padding-left:1rem; }
p,span,label,div { color:#000 !important; }
.stButton>button {
    background:linear-gradient(135deg,#2E7D32 0%,#4CAF50 100%) !important;
    color:white !important; border:none !important;
    border-radius:8px !important; font-weight:600 !important;
    transition:all 0.3s ease !important;
}
.stButton>button:hover {
    transform:translateY(-2px) !important;
    box-shadow:0 8px 20px rgba(46,125,50,0.3) !important;
}
.stMetric { background:white !important; border-radius:12px !important;
            padding:1.5rem !important; box-shadow:0 2px 8px rgba(0,0,0,0.08) !important; }
[data-testid="metric-container"]>div,
[data-testid="metric-container"] p { color:#000 !important; }
.stSidebar { background:linear-gradient(180deg,#FFFFFF 0%,#F9FAFB 100%) !important; }
.stTabs [data-baseweb="tab-list"] button { font-weight:600 !important; color:#6B7280 !important; }
.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
    color:#2E7D32 !important; border-bottom-color:#2E7D32 !important;
}
footer { visibility:hidden; }
#MainMenu { visibility:hidden; }
hr { border-color:#E5E7EB !important; }
</style>
""", unsafe_allow_html=True)

# ── session state ─────────────────────────────────────────────────────────────
init_session_state()

# ── page imports (lazy — only load what's needed) ─────────────────────────────
def _load_manager_home():
    from pages.manager_pages.home_dashboard     import show; return show

def _load_manager_single():
    from pages.manager_pages.single_prediction  import show; return show

def _load_manager_festival():
    from pages.manager_pages.festival_prediction import show; return show

def _load_manager_orders():
    from pages.manager_pages.orders_page        import show; return show

def _load_supplier_orders():
    from pages.supplier_pages.supplier_orders   import show; return show

def _load_supplier_analytics():
    from pages.supplier_pages.supplier_analytics import show; return show


# ── MANAGER NAV ───────────────────────────────────────────────────────────────
MANAGER_PAGES = [
    "🏠 Home",
    "📊 Single Prediction",
    "🎉 Festival Prediction",
    "📦 Orders",
]

SUPPLIER_PAGES = [
    "📤 Orders",
    "📊 Analytics",
]

ADMIN_PAGES = [
    "📊 MLOps Dashboard",
    "🏥 System Health",
]


# ── sidebar ───────────────────────────────────────────────────────────────────
def _render_sidebar() -> str:
    """Render sidebar and return selected page string."""
    with st.sidebar:
        # user card
        role_emoji = {"manager": "🏪", "supplier": "🚚", "admin": "⚙️"}
        emoji      = role_emoji.get(st.session_state.role, "👤")
        store_line = ""
        if st.session_state.role == "manager":
            sname      = STORE_NAMES.get(st.session_state.store_id, f"Store {st.session_state.store_id}")
            store_line = f"<p style='margin:4px 0 0;font-size:0.88rem;color:#555;'>🏪 {sname}</p>"

        st.markdown(f"""
            <div style="background:linear-gradient(135deg,rgba(46,125,50,0.08),rgba(76,175,80,0.04));
                        padding:1rem;border-radius:10px;margin-bottom:1.2rem;
                        border:1px solid #E5E7EB;">
                <p style="margin:0;font-weight:700;">{emoji} {st.session_state.user_email}</p>
                <p style="margin:4px 0 0;font-size:0.88rem;color:#555;">
                    Role: <strong>{st.session_state.role.title()}</strong>
                </p>
                {store_line}
            </div>
        """, unsafe_allow_html=True)

        st.divider()

        # navigation
        if st.session_state.role == "manager":
            st.markdown("**📋 Manager Menu**")
            default_idx = 0
            if "nav_override" in st.session_state:
                nav = st.session_state.pop("nav_override")
                if nav in MANAGER_PAGES:
                    default_idx = MANAGER_PAGES.index(nav)

            page = st.radio(
                "nav",
                MANAGER_PAGES,
                index=default_idx,
                label_visibility="collapsed",
                key="nav_manager",          # ← changed
            )

        elif st.session_state.role == "supplier":
            st.markdown("**📋 Supplier Menu**")
            page = st.radio(
                "nav",
                SUPPLIER_PAGES,
                label_visibility="collapsed",
                key="nav_supplier",          # ← changed
            )

        elif st.session_state.role == "admin":
            st.markdown("**📋 Admin Menu**")
            page = st.radio(
                "nav",
                ADMIN_PAGES,
                label_visibility="collapsed",
                key="nav_admin",             # ← changed
            )
        else:
            page = ""

        st.divider()

        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    return page


# ── main ──────────────────────────────────────────────────────────────────────
def main():
    if not st.session_state.logged_in:
        show_auth_page()
        return

    page = _render_sidebar()

    # ── MANAGER routing ────────────────────────────────────────────────────────
    if st.session_state.role == "manager":
        if page == "🏠 Home":
            _load_manager_home()()
        elif page == "📊 Single Prediction":
            _load_manager_single()()
        elif page == "🎉 Festival Prediction":
            _load_manager_festival()()
        elif page == "📦 Orders":
            _load_manager_orders()()

    # ── SUPPLIER routing ───────────────────────────────────────────────────────
    elif st.session_state.role == "supplier":
        if page == "📤 Orders":
            _load_supplier_orders()()
        elif page == "📊 Analytics":
            _load_supplier_analytics()()

    # ── ADMIN routing (Phase 3 placeholder) ───────────────────────────────────
    elif st.session_state.role == "admin":
      if page == "📊 MLOps Dashboard":
        from pages.admin_pages.mlops_dashboard import show
        show()

      elif page == "🏥 System Health":
        from pages.admin_pages.system_health import show
        show()


if __name__ == "__main__":
    main()