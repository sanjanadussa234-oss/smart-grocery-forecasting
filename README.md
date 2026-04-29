# 🛒 Smart Grocery Demand Forecasting System

A complete **end-to-end MLOps project** that predicts grocery product demand using machine learning, deployed via API, monitored in production, and supported with an automated retraining pipeline.

---

## Project Overview

Grocery demand is highly dynamic due to factors like pricing, promotions, seasonality, and customer behavior.  
This project builds a **real-world forecasting system** that:

- Predicts product demand at **store-item level**
- Provides **real-time predictions via API**
- Tracks model performance in production
- Detects drift and retrains automatically

---

## Key Features

- Real-time demand prediction (FastAPI)  
- Interactive UI (Streamlit)  
- Feature engineering (lags, seasonality, pricing)  
- Model monitoring (RMSE, drift detection, anomalies)  
- Automated retraining pipeline  
- CI/CD with GitHub Actions  
- Cloud deployment (Render)  

---

## System Architecture


User (Streamlit UI)
↓
FastAPI (Prediction API)
↓
ML Model (XGBoost)
↓
Prediction Logs (CSV)
↓
Monitoring System
↓
Drift Detection
↓
Retraining Pipeline


---

## 📂 Project Structure


smart-grocery-forecasting/
│
├── api/
│ └── main.py # FastAPI backend
│
├── mlops/
│ ├── monitor.py # Monitoring + drift detection
│ ├── retrain.py # Retraining pipeline
│
├── src/
│ └── train.py # Model training (with MLflow)
│
├── logs/
│ ├── predictions.csv # Model predictions
│ ├── actuals.csv # Simulated real-world data
│
├── models/
│ ├── xgboost_model.pkl
│ ├── feature_columns.json
│
├── data/
│ └── grocery_features.csv
│
├── app.py # Streamlit UI
├── requirements.txt
└── README.md


---

## Tech Stack

**Programming**
- Python

**Machine Learning**
- XGBoost  
- TensorFlow / Keras (optional LSTM)

**Data Processing**
- Pandas  
- NumPy  

**Backend**
- FastAPI  

**Frontend**
- Streamlit  

**Deployment**
- Render  

**CI/CD**
- GitHub Actions  

**Experiment Tracking**
- MLflow  

---

## Machine Learning Approach

### Feature Engineering
- Lag features: `lag_1`, `lag_7`, `lag_14`
- Price-based features
- Promotion & discount features
- Seasonal features (month, weekday)

### Model
- XGBoost Regressor

### Evaluation Metrics
- RMSE (Root Mean Square Error)
- MAE (Mean Absolute Error)

---

## 🔌 API Usage

### Endpoint:

POST /predict


### Sample Input:
```json
{
  "store_id_enc": 1,
  "item_id_enc": 2,
  "price": 20,
  "base_price": 25,
  "promotion": 1,
  "discount_pct": 10,
  "month": 4,
  "day_of_week": 2,
  "festival_flag": 0,
  "weekend": 0,
  "lag_1": 10,
  "lag_7": 12,
  "lag_14": 11
}
Response:
{
  "predicted_demand": 53.97
}
Monitoring System
The system tracks:
RMSE & MAE
Rolling RMSE (drift detection)
Anomaly detection (Z-score)
Item-level error analysis
Prediction trends

Retraining Pipeline
Automatically checks model performance
If RMSE > threshold:
Retrains model using full dataset
Saves updated model
Ensures model stays accurate over time

CI/CD Pipeline
Runs on every Git push
Validates environment setup
Ensures system reliability before deployment

Deployment
Backend deployed on Render (FastAPI)
UI deployed separately (Streamlit)
Auto-deploy enabled via GitHub integration

Future Improvements
Add PostgreSQL / MongoDB
Cloud storage (AWS S3)
ONNX model optimization
Advanced drift detection
CI/CD with full testing pipeline

Use Cases
Grocery store demand planning
Inventory optimization
Promotion strategy analysis
Reducing stockouts and wastage

Author:
Sanjana (M.Tech CSE)
Smart Grocery Demand Forecasting System

Final Note

This project demonstrates a complete MLOps lifecycle, including:

Model development
Deployment
Monitoring
Continuous improvement

It reflects real-world production systems used in retail analytics.