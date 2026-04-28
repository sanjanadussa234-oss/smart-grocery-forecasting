import pandas as pd
import numpy as np
import os
from datetime import datetime

import mlflow
import mlflow.tensorflow

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, r2_score

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout


# -------------------------------
# CONFIG
# -------------------------------
SEQ_LENGTH = 14   # last 14 days → predict next day
MODEL_NAME = "LSTM"
VERSION = "v1"


# -------------------------------
# CREATE SEQUENCES
# -------------------------------
def create_sequences(X, y, seq_length):
    Xs, ys = [], []

    for i in range(len(X) - seq_length):
        Xs.append(X[i:i+seq_length])
        ys.append(y[i+seq_length])

    return np.array(Xs), np.array(ys)


# -------------------------------
# MAIN FUNCTION
# -------------------------------
def train_lstm():

    mlflow.set_tracking_uri("file:./mlruns")
    mlflow.set_experiment("Grocery Demand Forecasting")

    run_name = f"{MODEL_NAME}_{VERSION}"

    print("📥 Loading dataset...")
    df = pd.read_csv("data/processed/grocery_features.csv")

    # -------------------------------
    # SORT (VERY IMPORTANT)
    # -------------------------------
    df = df.sort_values(["store_id_enc", "item_id_enc", "date"])

    # -------------------------------
    # FEATURES & TARGET
    # -------------------------------
    y = df["sales_units"].values
    X = df.drop(columns=["sales_units", "date"]).values

    # -------------------------------
    # SCALING (IMPORTANT FOR LSTM)
    # -------------------------------
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    # -------------------------------
    # CREATE SEQUENCES
    # -------------------------------
    print("⚙️ Creating sequences...")
    X_seq, y_seq = create_sequences(X_scaled, y, SEQ_LENGTH)

    print("Sequence Shape:", X_seq.shape)

    # -------------------------------
    # TRAIN-TEST SPLIT
    # -------------------------------
    split = int(len(X_seq) * 0.8)

    X_train, X_test = X_seq[:split], X_seq[split:]
    y_train, y_test = y_seq[:split], y_seq[split:]

    # -------------------------------
    # MODEL
    # -------------------------------
    print("\n🚀 Training LSTM...")

    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=(SEQ_LENGTH, X_train.shape[2])),
        Dropout(0.2),

        LSTM(32),
        Dropout(0.2),

        Dense(1)
    ])

    model.compile(
        optimizer="adam",
        loss="mse"
    )

    # -------------------------------
    # MLflow RUN
    # -------------------------------
    with mlflow.start_run(run_name=run_name):

        mlflow.log_param("model_name", MODEL_NAME)
        mlflow.log_param("version", VERSION)
        mlflow.log_param("sequence_length", SEQ_LENGTH)

        # -------------------------------
        # TRAIN
        # -------------------------------
        history = model.fit(
            X_train, y_train,
            epochs=5,
            batch_size=64,
            validation_split=0.1,
            verbose=1
        )

        # -------------------------------
        # PREDICT
        # -------------------------------
        y_pred = model.predict(X_test)

        # -------------------------------
        # METRICS
        # -------------------------------
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)

        print("\n📈 LSTM Performance:")
        print("RMSE:", round(rmse, 3))
        print("R2:", round(r2, 3))

        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2_score", r2)

        # -------------------------------
        # SAVE MODEL IN MLflow
        # -------------------------------
        mlflow.tensorflow.log_model(
            model,
            artifact_path="lstm_model"
        )

        # -------------------------------
        # SAVE LOCALLY (NO OVERWRITE)
        # -------------------------------
        os.makedirs("models", exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_path = f"models/lstm_{timestamp}.h5"

        model.save(model_path)

        print(f"\n💾 Model saved locally: {model_path}")
        print(f"✅ {run_name} logged in MLflow")


# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    train_lstm()