# ui/utils/config.py
"""
Configuration file with constants and API settings
"""

# ============================================
# API CONFIGURATION
# ============================================
API_BASE_URL = "http://localhost:8000"
API_ENDPOINTS = {
    "health": f"{API_BASE_URL}/",
    "predict": f"{API_BASE_URL}/predict",
    "predict_festival": f"{API_BASE_URL}/predict/festival",
}

# ============================================
# STORES
# ============================================
STORES = list(range(0, 8))  # 0-7
STORE_NAMES = {
    0: "Store 0 (Area 1)",
    1: "Store 1 (Area 1)",
    2: "Store 2 (Area 2)",
    3: "Store 3 (Area 2)",
    4: "Store 4 (Area 3)",
    5: "Store 5 (Area 3)",
    6: "Store 6 (Area 4)",
    7: "Store 7 (Area 4)",
}

AREAS = {
    "Area 1": [0, 1],
    "Area 2": [2, 3],
    "Area 3": [4, 5],
    "Area 4": [6, 7],
}

# ============================================
# FESTIVALS
# ============================================
FESTIVALS = [
    'christmas',
    'diwali',
    'eid',
    'holi',
    'independence day',
    'navratri',
    'new year',
    'none'
]

FESTIVAL_EMOJIS = {
    'christmas': '🎄',
    'diwali': '🪔',
    'eid': '🕌',
    'holi': '🌈',
    'independence day': '🇮🇳',
    'navratri': '🙏',
    'new year': '🎆',
    'none': '📅'
}

# ============================================
# CATEGORIES
# ============================================
CATEGORIES = [
    'Vegetables',
    'Fruits',
    'Dairy',
    'Beverages',
    'Grains',
    'Pulses',
    'Snacks'
]

# ============================================
# PATHS
# ============================================
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
UI_DIR = Path(__file__).parent.parent
DATA_DIR = UI_DIR / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
MODELS_DIR = PROJECT_ROOT / "models"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# CSV Files
USERS_CSV = DATA_DIR / "users.csv"
ORDERS_CSV = DATA_DIR / "orders.csv"
MONITORING_CSV = DATA_DIR / "monitoring.csv"

# Logs
SINGLE_PREDICTIONS_LOG = LOGS_DIR / "single_predictions.csv"
FESTIVAL_PREDICTIONS_LOG = LOGS_DIR / "festival_predictions.csv"
SINGLE_ACTUALS_LOG = LOGS_DIR / "single_actuals.csv"
FESTIVAL_ACTUALS_LOG = LOGS_DIR / "festival_actuals.csv"

# Models
FEATURE_COLUMNS_FILE = MODELS_DIR / "feature_columns.json"
MODEL_FILE = MODELS_DIR / "xgboost_model.pkl"

# ============================================
# UI SETTINGS
# ============================================
APP_TITLE = "🛒 Grocery Demand Forecasting"
APP_ICON = "🛒"

PRIMARY_COLOR = "#2E7D32"
SUCCESS_COLOR = "#10B981"
WARNING_COLOR = "#F59E0B"
DANGER_COLOR = "#EF4444"