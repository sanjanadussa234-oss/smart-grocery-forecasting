# src/config.py
"""
Configuration management for the entire MLOps pipeline
Centralized configuration for all modules
"""

import os
from pathlib import Path
from typing import Dict, List
import yaml

# ============================================
# PROJECT PATHS
# ============================================
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
FEATURES_DATA_DIR = DATA_DIR / "features"
DRIFT_DATA_DIR = DATA_DIR / "drift_data"
MODELS_DIR = PROJECT_ROOT / "models"
ARTIFACTS_DIR = MODELS_DIR / "artifacts"
MLFLOW_DIR = MODELS_DIR / "mlflow"
LOGS_DIR = PROJECT_ROOT / "logs"
METRICS_DIR = PROJECT_ROOT / "metrics"

# Create directories if they don't exist
for directory in [PROCESSED_DATA_DIR, FEATURES_DATA_DIR, DRIFT_DATA_DIR, 
                   ARTIFACTS_DIR, MLFLOW_DIR, LOGS_DIR, METRICS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ============================================
# DATA CONFIGURATION
# ============================================
class DataConfig:
    """Data processing configuration"""
    
    # Raw data
    RAW_DATA_FILE = RAW_DATA_DIR / "grocery_data.csv"
    PROCESSED_DATA_FILE = PROCESSED_DATA_DIR / "grocery_clean.csv"
    FEATURES_DATA_FILE = FEATURES_DATA_DIR / "grocery_features.csv"
    DRIFT_REFERENCE_FILE = DRIFT_DATA_DIR / "reference_data.csv"
    
    # Data parameters
    DATE_COLUMN = "date"
    TARGET_COLUMN = "sales_units"
    STORE_ID_COLUMN = "store_id"
    ITEM_ID_COLUMN = "item_id"
    
    # Categorical columns to encode
    CATEGORICAL_COLS = ["category"]
    
    # Numerical columns for scaling
    NUMERICAL_COLS = [
        "price", "base_price", "discount_pct", "promotion",
        "temperature_c", "rainfall_mm", "humidity_pct"
    ]
    
    # Missing value handling
    MISSING_VALUE_STRATEGY = {
        "sales_units": "forward_fill",  # Forward fill for target
        "price": "group_forward_fill",   # Forward fill by store-item
        "base_price": "group_forward_fill",
        "promotion": "zero",
        "discount_pct": "zero",
        "temperature_c": "interpolate",
        "rainfall_mm": "zero",
        "humidity_pct": "interpolate",
        "festival_flag": "zero"
    }
    
    # Outlier detection
    OUTLIER_METHOD = "iqr"  # "iqr" or "zscore"
    OUTLIER_THRESHOLD = 3.0
    
    # Data quality thresholds
    MIN_SAMPLES_PER_STORE_ITEM = 30
    MAX_MISSING_PCT = 0.3
    MIN_DATA_QUALITY_SCORE = 0.7

# ============================================
# FEATURE ENGINEERING CONFIGURATION
# ============================================
class FeatureConfig:
    """Feature engineering configuration"""
    
    # Lag features
    LAG_FEATURES = [1, 7, 14, 30]  # Historical demand
    
    # Rolling features
    ROLLING_WINDOWS = [7, 14, 30]
    ROLLING_STATS = ["mean", "std", "min", "max"]
    
    # Price-based features
    PRICE_FEATURES = ["price_diff", "price_ratio", "price_elasticity"]
    
    # Promotion features
    PROMO_FEATURES = ["promo_effect", "promo_intensity"]
    
    # Temporal features (cyclical encoding)
    CYCLICAL_FEATURES = {
        "month": 12,
        "day_of_week": 7,
        "day_of_month": 31
    }
    
    # Festival boost factors (by category)
    FESTIVAL_BOOST = {
        "Diwali": {"Snacks": 2.5, "Beverages": 2.2, "Pulses": 2.0, "Grains": 1.8},
        "Holi": {"Snacks": 2.0, "Beverages": 1.8, "Pulses": 1.5},
        "New Year": {"Beverages": 2.5, "Snacks": 2.0},
        "Ganesh Chaturthi": {"Snacks": 2.2, "Pulses": 1.8},
        "Navratri": {"Pulses": 2.5, "Snacks": 2.0, "Beverages": 1.5},
    }
    
    # Feature scaling
    SCALE_METHOD = "minmax"  # "minmax" or "standard"
    
    # Feature selection
    MIN_FEATURE_IMPORTANCE = 0.001
    MAX_FEATURES = None  # None = use all

# ============================================
# MODEL TRAINING CONFIGURATION
# ============================================
class ModelConfig:
    """XGBoost model training configuration"""
    
    # Model type
    MODEL_TYPE = "xgboost"  # Changed from LSTM
    MODEL_NAME = "XGBoost_GroceryDemand"
    MODEL_VERSION = "v2.0"
    
    # XGBoost hyperparameters
    XGBOOST_PARAMS = {
        "objective": "reg:squarederror",
        "max_depth": 6,
        "learning_rate": 0.1,
        "n_estimators": 100,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "min_child_weight": 1,
        "gamma": 0,
        "reg_alpha": 0.0,
        "reg_lambda": 1.0,
        "random_state": 42,
        "n_jobs": -1,
        "verbose": 0
    }
    
    # Training parameters
    TRAIN_TEST_SPLIT = 0.8
    VALIDATION_SPLIT = 0.2
    CROSS_VALIDATION_FOLDS = 5
    
    # Early stopping
    EARLY_STOPPING_ROUNDS = 50
    EARLY_STOPPING_METRIC = "rmse"
    
    # Hyperparameter tuning
    HYPERPARAMETER_TUNING = {
        "enabled": True,
        "method": "optuna",  # "optuna" or "gridsearch"
        "n_trials": 100,
        "params_to_tune": {
            "max_depth": [4, 6, 8, 10],
            "learning_rate": [0.01, 0.05, 0.1, 0.2],
            "n_estimators": [50, 100, 200, 300],
        }
    }
    
    # Model artifacts
    MODEL_FILE = ARTIFACTS_DIR / "xgboost_model.pkl"
    SCALER_FILE = ARTIFACTS_DIR / "scaler.pkl"
    LABEL_ENCODERS_FILE = ARTIFACTS_DIR / "label_encoders.pkl"
    FEATURE_COLUMNS_FILE = ARTIFACTS_DIR / "feature_columns.json"
    MODEL_METADATA_FILE = ARTIFACTS_DIR / "model_metadata.json"

# ============================================
# DRIFT DETECTION CONFIGURATION
# ============================================
class DriftConfig:
    """Data and model drift detection configuration"""
    
    # Data drift detection
    DATA_DRIFT_METHOD = "ks"  # "ks" (Kolmogorov-Smirnov), "chi2", or "wasserstein"
    DATA_DRIFT_THRESHOLD = 0.05  # p-value threshold for statistical test
    DATA_DRIFT_WINDOW = 100  # Number of samples to check drift on
    
    # Feature-level drift
    FEATURE_DRIFT_THRESHOLD = 0.05
    FEATURE_DRIFT_METHOD = "ks"
    
    # Model drift detection
    MODEL_DRIFT_METHOD = "performance"  # "performance" or "prediction_distribution"
    MODEL_DRIFT_THRESHOLD = 0.1  # 10% performance drop triggers alert
    
    # Drift monitoring metrics
    MONITOR_METRICS = ["rmse", "mae", "r2", "mape"]
    
    # Reference data
    DRIFT_REFERENCE_SAMPLES = 1000  # Samples used as reference
    
    # Drift detection frequency
    CHECK_DRIFT_EVERY_N_PREDICTIONS = 100
    CHECK_DRIFT_DAILY = True

# ============================================
# MONITORING CONFIGURATION
# ============================================
class MonitoringConfig:
    """System monitoring and alerting configuration"""
    
    # Prediction logging
    LOG_PREDICTIONS = True
    PREDICTION_LOG_FILE = METRICS_DIR / "prediction_logs.csv"
    
    # Performance metrics
    METRICS_FILE = METRICS_DIR / "model_performance.csv"
    QUALITY_METRICS_FILE = METRICS_DIR / "data_quality_metrics.csv"
    
    # Alert thresholds
    ALERT_THRESHOLDS = {
        "prediction_latency_ms": 200,  # Alert if > 200ms
        "model_accuracy_drop": 0.1,     # Alert if accuracy drops > 10%
        "data_quality_score": 0.7,      # Alert if < 0.7
        "missing_value_pct": 0.3,       # Alert if > 30% missing
        "error_rate": 0.05,             # Alert if > 5% errors
    }
    
    # Monitoring intervals
    MONITOR_INTERVAL_MINUTES = 60
    GENERATE_REPORT_DAILY = True
    REPORT_TIME = "23:00"  # Generate report at 11 PM

# ============================================
# MLFLOW CONFIGURATION
# ============================================
class MLFlowConfig:
    """MLflow experiment tracking configuration"""
    
    # MLflow tracking
    TRACKING_URI = f"file:{MLFLOW_DIR}"
    EXPERIMENT_NAME = "Grocery_Demand_Forecasting"
    RUN_NAME_PREFIX = "xgboost"
    
    # Auto-logging
    AUTOLOG = True
    
    # Artifacts
    ARTIFACT_PATH = "models"
    
    # Registered model
    REGISTERED_MODEL_NAME = "grocery-demand-xgboost"

# ============================================
# API CONFIGURATION
# ============================================
class APIConfig:
    """FastAPI configuration"""
    
    # Server
    HOST = "0.0.0.0"
    PORT = 8000
    DEBUG = False
    
    # API settings
    API_PREFIX = "/api/v1"
    TITLE = "Smart Grocery Demand Forecasting API"
    DESCRIPTION = "MLOps-enabled REST API for grocery demand prediction"
    VERSION = "1.0.0"
    
    # Security
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # Rate limiting
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_REQUESTS = 100  # per window
    RATE_LIMIT_WINDOW = 60  # seconds
    
    # CORS
    CORS_ORIGINS = ["*"]  # Change in production
    CORS_CREDENTIALS = True
    CORS_METHODS = ["*"]
    CORS_HEADERS = ["*"]

# ============================================
# DATABASE CONFIGURATION
# ============================================
class DatabaseConfig:
    """Database configuration"""
    
    # Database type: "sqlite" or "postgresql"
    DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite")
    
    # SQLite
    SQLITE_DB_FILE = PROJECT_ROOT / "grocery_demand.db"
    SQLITE_URL = f"sqlite:///{SQLITE_DB_FILE}"
    
    # PostgreSQL
    POSTGRESQL_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRESQL_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRESQL_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRESQL_PORT = os.getenv("POSTGRES_PORT", "5432")
    POSTGRESQL_DB = os.getenv("POSTGRES_DB", "grocery_demand")
    POSTGRESQL_URL = (
        f"postgresql://{POSTGRESQL_USER}:{POSTGRESQL_PASSWORD}@"
        f"{POSTGRESQL_HOST}:{POSTGRESQL_PORT}/{POSTGRESQL_DB}"
    )
    
    # Connection
    DATABASE_URL = SQLITE_URL if DATABASE_TYPE == "sqlite" else POSTGRESQL_URL
    ECHO = False
    POOL_SIZE = 5
    MAX_OVERFLOW = 10

# ============================================
# LOGGING CONFIGURATION
# ============================================
class LoggingConfig:
    """Logging configuration"""
    
    # Log files
    APP_LOG_FILE = LOGS_DIR / "app.log"
    TRAINING_LOG_FILE = LOGS_DIR / "training.log"
    PREDICTION_LOG_FILE = LOGS_DIR / "predictions.log"
    DRIFT_LOG_FILE = LOGS_DIR / "drift.log"
    ERROR_LOG_FILE = LOGS_DIR / "errors.log"
    
    # Log level
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Log format
    LOG_FORMAT = (
        "%(asctime)s - %(name)s - %(levelname)s - "
        "%(filename)s:%(lineno)d - %(message)s"
    )
    
    # Log rotation
    MAX_LOG_SIZE_MB = 10
    BACKUP_COUNT = 5

# ============================================
# DEPLOYMENT CONFIGURATION
# ============================================
class DeploymentConfig:
    """Deployment configuration"""
    
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")  # development, staging, production
    
    # Docker
    DOCKER_ENABLED = True
    DOCKER_IMAGE_NAME = "grocery-demand-forecasting"
    DOCKER_IMAGE_TAG = "latest"
    
    # Kubernetes
    KUBERNETES_ENABLED = False  # Set to True for K8s deployment
    KUBERNETES_NAMESPACE = "default"
    
    # Cloud deployment
    CLOUD_PROVIDER = None  # "aws", "gcp", "azure"
    CLOUD_REGION = None
    CLOUD_CREDENTIALS_FILE = None

# ============================================
# MASTER CONFIGURATION CLASS
# ============================================
class Config:
    """Master configuration class combining all configs"""
    
    # Sub-configs
    data = DataConfig
    feature = FeatureConfig
    model = ModelConfig
    drift = DriftConfig
    monitoring = MonitoringConfig
    mlflow = MLFlowConfig
    api = APIConfig
    database = DatabaseConfig
    logging = LoggingConfig
    deployment = DeploymentConfig
    
    # Project metadata
    PROJECT_NAME = "Smart Grocery Demand Forecasting"
    PROJECT_DESCRIPTION = "MLOps-enabled demand forecasting system for retail stores"
    PROJECT_VERSION = "2.0.0"
    
    @staticmethod
    def load_yaml_config(config_file: str) -> Dict:
        """Load configuration from YAML file"""
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    
    @staticmethod
    def save_yaml_config(config_data: Dict, config_file: str):
        """Save configuration to YAML file"""
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False)

# ============================================
# CONVENIENCE IMPORTS
# ============================================
# Easy access to configs
config = Config()