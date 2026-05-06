# ui/utils/auth.py
"""
Authentication system for Manager and Supplier
Handles login, signup, and credential verification
FIXED:
  - store_id dtype mismatch (CSV reads float, compare needs int)
  - password_hash whitespace stripping
  - robust CSV loading with dtype enforcement
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import hashlib

# ============================================
# PATHS
# ============================================
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
CREDENTIALS_FILE = DATA_DIR / "users.csv"

# ============================================
# CSV DTYPE MAP  ← KEY FIX
# Always enforce these dtypes on load so store_id
# never becomes float and password_hash never gets
# mangled by pandas type inference.
# ============================================
_CSV_DTYPES = {
    "email":         str,
    "password_hash": str,
    "role":          str,
    "store_id":      "Int64",   # nullable integer – survives round-trip
    "created_at":    str,
}

_EMPTY_COLUMNS = list(_CSV_DTYPES.keys())


# ============================================
# INITIALIZE CREDENTIALS FILE
# ============================================
def init_credentials_file():
    """Initialize users CSV if it doesn't exist or is corrupted."""
    if not CREDENTIALS_FILE.exists():
        _write_empty_csv()
        return

    try:
        df = _load_csv()
        if df.empty:
            _write_empty_csv()
    except Exception:
        _write_empty_csv()


def _write_empty_csv():
    pd.DataFrame(columns=_EMPTY_COLUMNS).to_csv(CREDENTIALS_FILE, index=False)


def _load_csv() -> pd.DataFrame:
    """
    Load users CSV with enforced dtypes.
    Returns an empty DataFrame (correct columns) on any read error.
    """
    try:
        df = pd.read_csv(
            CREDENTIALS_FILE,
            dtype=_CSV_DTYPES,
            keep_default_na=False,   # stops pandas turning empty strings → NaN
        )
        # Strip accidental whitespace from string columns
        for col in ["email", "password_hash", "role"]:
            if col in df.columns:
                df[col] = df[col].str.strip()
        return df
    except (pd.errors.EmptyDataError, pd.errors.ParserError, FileNotFoundError):
        return pd.DataFrame(columns=_EMPTY_COLUMNS)


# ============================================
# HELPER FUNCTIONS
# ============================================
def hash_password(password: str) -> str:
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def validate_email(email: str) -> bool:
    """Basic email validation."""
    return "@" in email and "." in email


# ============================================
# SAVE USERS
# ============================================
def save_manager(email: str, password: str, store_id: int) -> tuple:
    """Save new manager credentials."""
    init_credentials_file()
    df = _load_csv()

    if not validate_email(email):
        return False, "❌ Invalid email format"
    if email in df["email"].values:
        return False, "❌ Email already registered"
    if len(password) < 6:
        return False, "❌ Password must be at least 6 characters"
    if store_id < 0 or store_id > 7:
        return False, "❌ Invalid store ID (must be 0–7)"

    # Check if manager already exists for this store
    existing = df[(df["role"] == "manager") & (df["store_id"] == store_id)]
    if not existing.empty:
        return False, f"❌ Store {store_id} already has a manager"

    new_row = pd.DataFrame([{
        "email":         email.strip(),
        "password_hash": hash_password(password),
        "role":          "manager",
        "store_id":      int(store_id),
        "created_at":    datetime.now().isoformat(),
    }])

    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(CREDENTIALS_FILE, index=False)
    return True, "✅ Manager account created successfully!"


def save_supplier(email: str, password: str) -> tuple:
    """Save new supplier credentials."""
    init_credentials_file()
    df = _load_csv()

    if not validate_email(email):
        return False, "❌ Invalid email format"
    if email in df["email"].values:
        return False, "❌ Email already registered"
    if len(password) < 6:
        return False, "❌ Password must be at least 6 characters"

    new_row = pd.DataFrame([{
        "email":         email.strip(),
        "password_hash": hash_password(password),
        "role":          "supplier",
        "store_id":      -1,
        "created_at":    datetime.now().isoformat(),
    }])

    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(CREDENTIALS_FILE, index=False)
    return True, "✅ Supplier account created successfully!"

def save_admin(email: str, password: str) -> tuple:
    """Save new admin credentials."""
    init_credentials_file()
    df = _load_csv()

    if not validate_email(email):
        return False, "❌ Invalid email format"
    if email in df["email"].values:
        return False, "❌ Email already registered"
    if len(password) < 6:
        return False, "❌ Password must be at least 6 characters"

    new_row = pd.DataFrame([{
        "email": email.strip(),
        "password_hash": hash_password(password),
        "role": "admin",
        "store_id": -1,
        "created_at": datetime.now().isoformat(),
    }])

    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(CREDENTIALS_FILE, index=False)

    return True, "✅ Admin account created successfully!"

# ============================================
# VERIFY LOGIN
# ============================================
def verify_manager_login(email: str, password: str, store_id: int) -> tuple:
    """Verify manager login credentials."""
    init_credentials_file()
    df = _load_csv()

    user_row = df[(df["email"] == email.strip()) & (df["role"] == "manager")]
    if user_row.empty:
        return False, None, "❌ Manager account not found"

    user = user_row.iloc[0]

    # ── PASSWORD CHECK ──────────────────────────────────────────────────────
    stored_hash = str(user["password_hash"]).strip()
    entered_hash = hash_password(password)
    if stored_hash != entered_hash:
        return False, None, "❌ Incorrect password"

    # ── STORE ID CHECK  (cast both sides to int) ────────────────────────────
    try:
        stored_store = int(user["store_id"])
    except (ValueError, TypeError):
        stored_store = -1

    if stored_store != int(store_id):
        return False, None, f"❌ Store ID mismatch (your store: {stored_store})"

    return True, user.to_dict(), "✅ Login successful"


def verify_supplier_login(email: str, password: str) -> tuple:
    """Verify supplier login credentials."""
    init_credentials_file()
    df = _load_csv()

    user_row = df[(df["email"] == email.strip()) & (df["role"] == "supplier")]
    if user_row.empty:
        return False, None, "❌ Supplier account not found"

    user = user_row.iloc[0]

    stored_hash = str(user["password_hash"]).strip()
    if stored_hash != hash_password(password):
        return False, None, "❌ Incorrect password"

    return True, user.to_dict(), "✅ Login successful"

def verify_admin_login(email: str, password: str) -> tuple:
    """Verify admin login credentials."""
    init_credentials_file()
    df = _load_csv()

    user_row = df[(df["email"] == email.strip()) & (df["role"] == "admin")]

    if user_row.empty:
        return False, None, "❌ Admin account not found"

    user = user_row.iloc[0]

    stored_hash = str(user["password_hash"]).strip()
    if stored_hash != hash_password(password):
        return False, None, "❌ Incorrect password"

    return True, user.to_dict(), "✅ Admin login successful"
# ============================================
# SHOW AUTH PAGE
# ============================================
def show_auth_page():
    """Display authentication page with login/signup."""

    st.markdown("""
        <div style="text-align: center; margin-top: 60px; margin-bottom: 40px;">
            <h1 style="color: #2E7D32; font-size: 3.5rem; margin: 0;">🛒</h1>
            <h1 style="color: #2E7D32; margin-top: 0.5rem; margin-bottom: 0.5rem;">
                Grocery Demand Forecasting
            </h1>
            <p style="color: #6B7280; font-size: 1.1rem; margin: 0;">
                AI-Powered Inventory &amp; Order Management
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_login, tab_signup = st.tabs(["🔐 Login", "📝 Sign Up"])

        # ── LOGIN ──────────────────────────────────────────────────────────
        with tab_login:
            st.markdown("### Choose Your Role")

            login_role = st.radio(
                "I am a:",
                ["Store Manager", "Supplier", "Admin"],
                horizontal=True,
                label_visibility="collapsed",
                key="login_role",
            )

            st.divider()

            email = st.text_input(
                "Email Address",
                placeholder="your.email@example.com",
                key="login_email",
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                key="login_password",
            )

            if login_role == "Store Manager":
                store_id = st.number_input(
                    "Store ID",
                    min_value=0,
                    max_value=7,
                    value=0,
                    help="Your assigned store ID (0-7)",
                    key="login_store_id",
                )
            else:
                store_id = None

            st.divider()

            if st.button("🔓 Login", use_container_width=True, type="primary"):
                if not email or not password:
                    st.error("❌ Please enter email and password")
                    st.stop()

                if login_role == "Store Manager":
                 success, user_data, message = verify_manager_login(
                 email, password, int(store_id)
                 )

                elif login_role == "Supplier":
                  success, user_data, message = verify_supplier_login(email, password)

                else:  # Admin
                  success, user_data, message = verify_admin_login(email, password)

                if success:
                    st.session_state.logged_in  = True
                    st.session_state.user_email = email
                    if login_role == "Store Manager":
                      st.session_state.role = "manager"
                    elif login_role == "Supplier":
                      st.session_state.role = "supplier"
                    else:
                      st.session_state.role = "admin"
                    st.session_state.store_id   = int(store_id) if login_role == "Store Manager" else None
                    st.session_state.user_data  = user_data
                    st.success(message)
                    st.balloons()
                    st.rerun()
                else:
                    st.error(message)

        # ── SIGN UP ────────────────────────────────────────────────────────
        with tab_signup:
            st.markdown("### Create New Account")

            signup_role = st.radio(
                "Register as:",
                ["Store Manager", "Supplier", "Admin"],
                horizontal=True,
                label_visibility="collapsed",
                key="signup_role",
            )

            st.divider()

            signup_email = st.text_input(
                "Email Address",
                placeholder="your.email@example.com",
                key="signup_email",
            )
            signup_password = st.text_input(
                "Password",
                type="password",
                placeholder="Create a strong password",
                help="Minimum 6 characters",
                key="signup_password",
            )
            signup_password_confirm = st.text_input(
                "Confirm Password",
                type="password",
                placeholder="Re-enter your password",
                key="signup_password_confirm",
            )

            if signup_role == "Store Manager":
                signup_store_id = st.number_input(
                    "Store ID",
                    min_value=0,
                    max_value=7,
                    value=0,
                    help="Your assigned store ID (0-7). Cannot be changed later!",
                    key="signup_store_id",
                )
            else:
                signup_store_id = None

            st.caption("✓ Minimum 6 characters")
            st.divider()

            if st.button("📝 Create Account", use_container_width=True, type="primary"):
                if not signup_email or not signup_password:
                    st.error("❌ Please fill all fields")
                    st.stop()
                if signup_password != signup_password_confirm:
                    st.error("❌ Passwords do not match")
                    st.stop()
                if len(signup_password) < 6:
                    st.error("❌ Password must be at least 6 characters")
                    st.stop()

                if signup_role == "Store Manager":
                 success, message = save_manager(
                 signup_email, signup_password, int(signup_store_id)
                )

                elif signup_role == "Supplier":
                 success, message = save_supplier(
                 signup_email, signup_password
                )

                else:  # Admin
                 success, message = save_admin(
                 signup_email, signup_password
                )

                if success:
                    st.success(message)
                    st.info("✅ You can now login with your credentials")
                    st.balloons()
                else:
                    st.error(message)


# ============================================
# INITIALIZE SESSION STATE
# ============================================
def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        "logged_in":           False,
        "user_email":          None,
        "role":                None,
        "store_id":            None,
        "user_data":           None,
        "predictions_history": [],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val