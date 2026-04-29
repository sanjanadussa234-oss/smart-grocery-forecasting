import joblib
import numpy as np
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

# ========================
# LOAD MODEL
# ========================
model = joblib.load("models/xgboost_model.pkl")

# ========================
# FIX: Wrap model
# ========================
# convert expects sklearn-compatible pipeline
initial_type = [('input', FloatTensorType([None, model.n_features_in_]))]

# ========================
# CONVERT
# ========================
onnx_model = convert_sklearn(model, initial_types=initial_type)

# ========================
# SAVE
# ========================
with open("models/model.onnx", "wb") as f:
    f.write(onnx_model.SerializeToString())

print("✅ ONNX model created successfully!")