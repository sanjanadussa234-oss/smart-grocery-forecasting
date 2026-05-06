# ui/utils/__init__.py
"""
Utilities package for UI — Phase 2
"""

from .auth       import init_session_state, show_auth_page
from .config     import API_BASE_URL, STORES, FESTIVALS
from .api_client import predict_single, predict_festival, check_api_health
from .orders_db  import (
    create_order,
    get_orders_for_store,
    get_all_orders,
    get_active_orders,
    get_completed_orders,
    update_order_status,
    cancel_order,
    get_order_stats_for_store,
    get_global_order_stats,
)

__all__ = [
    # auth
    "init_session_state",
    "show_auth_page",
    # config
    "API_BASE_URL",
    "STORES",
    "FESTIVALS",
    # api_client
    "predict_single",
    "predict_festival",
    "check_api_health",
    # orders_db
    "create_order",
    "get_orders_for_store",
    "get_all_orders",
    "get_active_orders",
    "get_completed_orders",
    "update_order_status",
    "cancel_order",
    "get_order_stats_for_store",
    "get_global_order_stats",
]