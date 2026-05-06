# ui/utils/api_client.py
"""
FastAPI client — all HTTP calls to the backend go through here.
Never import requests directly in page modules; use this instead.
"""

import requests
# from datetime import date
# from typing import Optional
# datetime and Optional no longer needed
from .config import API_ENDPOINTS

# ── timeout (seconds) ────────────────────────────────────────────────────────
_TIMEOUT = 10


# ============================================================
# HEALTH CHECK
# ============================================================
def check_api_health() -> dict:
    """
    Returns {"status": "ok"} or {"status": "error", "message": "..."}
    """
    try:
        r = requests.get(API_ENDPOINTS["health"], timeout=_TIMEOUT)
        if r.status_code == 200:
            return {"status": "ok"}
        return {"status": "error", "message": f"HTTP {r.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"status": "error", "message": "Cannot reach API — is FastAPI running?"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================
# SINGLE ITEM PREDICTION
# ============================================================
def predict_single(
    store_id: int,
    item_name: str,
    category: str,
    current_stock: float = 0.0,
    festival: str = "none",
    has_discount: bool = False,
    discount_pct: float = 0.0,
    has_promotion: bool = False,
    promotion: int = 0,
) -> dict:
    """
    POST /predict

    Returns on success:
        {
            "success": True,
            "predicted_demand": float,
            "item_name": str,
            "store_id": int,
            "date": str,
            "festival": str,
        }
    Returns on failure:
        {
            "success": False,
            "error": str,
        }
    """
    payload = {
        "item_name":      item_name,
        "category":       category,
        "store_id":       int(store_id),
        "current_stock":  float(current_stock),
        "is_festival":    festival != "none",
        "festival_name":  festival,
        "has_discount":   has_discount,
        "discount_pct":   float(discount_pct),
        "has_promotion":  has_promotion,
        "promotion":      int(promotion),
    }
    try:
        r = requests.post(API_ENDPOINTS["predict"], json=payload, timeout=_TIMEOUT)
        if r.status_code == 200:
            data = r.json()
            data["success"] = True
            return data
        # API returned an error body
        try:
            detail = r.json().get("detail", r.text)
        except Exception:
            detail = r.text
        return {"success": False, "error": f"API error {r.status_code}: {detail}"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Cannot reach API — is FastAPI running?"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================
# FESTIVAL PREDICTION
# ============================================================
def predict_festival(
    store_id: int,
    festival: str,
    top_n: int = 5,
    has_discount: bool = False,
    discount_pct: float = 0.0,
    has_promotion: bool = False,
    promotion: int = 0,
) -> dict:
    """
    POST /predict/festival

    Returns on success:
        {
            "success": True,
            "festival": str,
            "store_id": int,
            "predictions": [ { "item_name": str, "category": str,
                                "predicted_demand": float }, ... ]
        }
    Returns on failure:
        {
            "success": False,
            "error": str,
        }
    """
    payload = {
        "festival_name":  festival,
        "store_id":       int(store_id),
        "top_n":          top_n,
        "has_discount":   has_discount,
        "discount_pct":   float(discount_pct),
        "has_promotion":  has_promotion,
        "promotion":      int(promotion),
    }
    try:
        r = requests.post(API_ENDPOINTS["predict_festival"], json=payload, timeout=_TIMEOUT)
        if r.status_code == 200:
            data = r.json()
            # FastAPI returns a list directly for festival predictions
            if isinstance(data, list):
                return {"success": True, "predictions": data}
            data["success"] = True
            return data
        try:
            detail = r.json().get("detail", r.text)
        except Exception:
            detail = r.text
        return {"success": False, "error": f"API error {r.status_code}: {detail}"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Cannot reach API — is FastAPI running?"}
    except Exception as e:
        return {"success": False, "error": str(e)}