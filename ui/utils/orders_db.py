# ui/utils/orders_db.py
"""
CSV-based order management.
All order read/write operations go through here — never touch orders.csv directly
from page modules.

Order statuses:
    pending    → placed by manager, waiting for supplier
    accepted   → supplier accepted
    dispatched → supplier dispatched
    delivered  → supplier marked delivered
    cancelled  → cancelled by either party
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import uuid

# ── paths ─────────────────────────────────────────────────────────────────────
DATA_DIR   = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
ORDERS_CSV = DATA_DIR / "orders.csv"

# ── schema ────────────────────────────────────────────────────────────────────
_COLUMNS = [
    "order_id",        # UUID string
    "store_id",        # int
    "manager_email",   # str
    "item_name",       # str
    "category",        # str
    "quantity",        # float  (predicted demand units)
    "unit_price",      # float
    "total_price",     # float
    "festival",        # str ("none" or festival name)
    "prediction_date", # str  (ISO date)
    "status",          # str  (pending/accepted/dispatched/delivered/cancelled)
    "notes",           # str
    "created_at",      # str  (ISO datetime)
    "updated_at",      # str  (ISO datetime)
]

_DTYPES = {
    "order_id":        str,
    "store_id":        "Int64",
    "manager_email":   str,
    "item_name":       str,
    "category":        str,
    "quantity":        float,
    "unit_price":      float,
    "total_price":     float,
    "festival":        str,
    "prediction_date": str,
    "status":          str,
    "notes":           str,
    "created_at":      str,
    "updated_at":      str,
}

VALID_STATUSES = {"pending", "accepted", "dispatched", "delivered", "cancelled"}


# ── internal helpers ──────────────────────────────────────────────────────────
def _init_csv():
    if not ORDERS_CSV.exists():
        pd.DataFrame(columns=_COLUMNS).to_csv(ORDERS_CSV, index=False)


def _load() -> pd.DataFrame:
    _init_csv()
    try:
        df = pd.read_csv(ORDERS_CSV, dtype=_DTYPES, keep_default_na=False)
        # ensure all expected columns exist (forward-compat)
        for col in _COLUMNS:
            if col not in df.columns:
                df[col] = ""
        return df[_COLUMNS]
    except (pd.errors.EmptyDataError, pd.errors.ParserError):
        return pd.DataFrame(columns=_COLUMNS)


def _save(df: pd.DataFrame):
    df.to_csv(ORDERS_CSV, index=False)


# ── PUBLIC API ────────────────────────────────────────────────────────────────

def create_order(
    store_id: int,
    manager_email: str,
    item_name: str,
    category: str,
    quantity: float,
    unit_price: float,
    festival: str = "none",
    prediction_date: str = "",
    notes: str = "",
) -> dict:
    """
    Create a new order with status='pending'.
    Returns {"success": True, "order_id": str} or {"success": False, "error": str}
    """
    df = _load()
    now = datetime.now().isoformat()
    order_id = str(uuid.uuid4())[:8].upper()   # short readable ID

    new_row = {
        "order_id":        order_id,
        "store_id":        int(store_id),
        "manager_email":   manager_email,
        "item_name":       item_name,
        "category":        category,
        "quantity":        float(quantity),
        "unit_price":      float(unit_price),
        "total_price":     round(float(quantity) * float(unit_price), 2),
        "festival":        festival,
        "prediction_date": prediction_date,
        "status":          "pending",
        "notes":           notes,
        "created_at":      now,
        "updated_at":      now,
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    _save(df)
    return {"success": True, "order_id": order_id}


def get_orders_for_store(store_id: int) -> pd.DataFrame:
    """All orders for a specific store (manager view)."""
    df = _load()
    return df[df["store_id"] == int(store_id)].copy().reset_index(drop=True)


def get_all_orders() -> pd.DataFrame:
    """All orders across all stores (supplier view)."""
    return _load()


def get_pending_orders() -> pd.DataFrame:
    """Pending orders — supplier sees these to act on."""
    df = _load()
    return df[df["status"] == "pending"].copy().reset_index(drop=True)


def get_active_orders() -> pd.DataFrame:
    """Active = pending + accepted + dispatched."""
    df = _load()
    active = df[df["status"].isin(["pending", "accepted", "dispatched"])]
    return active.copy().reset_index(drop=True)


def get_completed_orders() -> pd.DataFrame:
    """Completed = delivered + cancelled."""
    df = _load()
    done = df[df["status"].isin(["delivered", "cancelled"])]
    return done.copy().reset_index(drop=True)


def update_order_status(order_id: str, new_status: str, notes: str = "") -> dict:
    """
    Update an order's status.
    Returns {"success": True} or {"success": False, "error": str}
    """
    if new_status not in VALID_STATUSES:
        return {"success": False, "error": f"Invalid status '{new_status}'"}

    df = _load()
    mask = df["order_id"] == order_id

    if not mask.any():
        return {"success": False, "error": f"Order {order_id} not found"}

    df.loc[mask, "status"]     = new_status
    df.loc[mask, "updated_at"] = datetime.now().isoformat()
    if notes:
        df.loc[mask, "notes"] = notes

    _save(df)
    return {"success": True}


def cancel_order(order_id: str, reason: str = "") -> dict:
    """Convenience wrapper for cancellation."""
    return update_order_status(order_id, "cancelled", notes=reason)


def get_order_stats_for_store(store_id: int) -> dict:
    """
    Summary counts for the manager home dashboard.
    """
    df = get_orders_for_store(store_id)
    if df.empty:
        return {
            "total":      0,
            "pending":    0,
            "active":     0,
            "delivered":  0,
            "cancelled":  0,
            "total_value": 0.0,
        }
    return {
        "total":       len(df),
        "pending":     int((df["status"] == "pending").sum()),
        "active":      int(df["status"].isin(["accepted", "dispatched"]).sum()),
        "delivered":   int((df["status"] == "delivered").sum()),
        "cancelled":   int((df["status"] == "cancelled").sum()),
        "total_value": round(df["total_price"].astype(float).sum(), 2),
    }


def get_global_order_stats() -> dict:
    """Summary counts for supplier dashboard."""
    df = _load()
    if df.empty:
        return {
            "total":      0,
            "pending":    0,
            "active":     0,
            "delivered":  0,
            "cancelled":  0,
            "total_value": 0.0,
        }
    return {
        "total":       len(df),
        "pending":     int((df["status"] == "pending").sum()),
        "active":      int(df["status"].isin(["accepted", "dispatched"]).sum()),
        "delivered":   int((df["status"] == "delivered").sum()),
        "cancelled":   int((df["status"] == "cancelled").sum()),
        "total_value": round(df["total_price"].astype(float).sum(), 2),
    }