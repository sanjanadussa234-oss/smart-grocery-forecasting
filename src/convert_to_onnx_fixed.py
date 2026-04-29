import joblib
import onnxmltools
from onnxmltools.convert.common.data_types import FloatTensorType

# ========================
# LOAD MODEL
# ========================
model = joblib.load("models/xgboost_model.pkl")

# 🔥 STEP 1: get booster
booster = model.get_booster()

# 🔥 STEP 2: REMOVE FEATURE NAMES (THIS IS THE REAL FIX)
booster.feature_names = None

# ========================
# INPUT SHAPE
# ========================
n_features = model.n_features_in_
initial_type = [("input", FloatTensorType([None, n_features]))]

# ========================
# CONVERT
# ========================
onnx_model = onnxmltools.convert_xgboost(
    booster,
    initial_types=initial_type
)

# ========================
# SAVE
# ========================
with open("models/model.onnx", "wb") as f:
    f.write(onnx_model.SerializeToString())

print("✅ ONNX model saved successfully!")