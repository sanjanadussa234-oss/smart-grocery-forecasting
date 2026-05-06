# ui/__init__.py
"""
Smart Grocery Demand Forecasting System - UI Package
"""

__version__ = "1.0.0"
__author__ = "Your Name"

# ui/utils/__init__.py
"""
Utilities package for UI
"""

from .auth import init_session_state, show_auth_page
from .config import API_BASE_URL, STORES, FESTIVALS

__all__ = [
    'init_session_state',
    'show_auth_page',
    'API_BASE_URL',
    'STORES',
    'FESTIVALS'
]

# ui/pages/__init__.py
"""
Pages package for UI
"""

# ui/pages/manager_pages/__init__.py
"""
Manager pages package
"""

# ui/pages/supplier_pages/__init__.py
"""
Supplier pages package
"""

# ui/pages/admin_pages/__init__.py
"""
Admin pages package
"""