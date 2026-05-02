import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import xgboost as xgb

# -------------------------------------------------
# PATH SETUP
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "Data")
LOG_DIR = os.path.join(BASE_DIR, "logs")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

os.makedirs(OUTPUT_DIR, exist_ok=True)


# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
def load_data():
    predictions_path = os.path.join(DATA_DIR, "predictions.csv")
    actuals_path = os.path.join(DATA_DIR, "actuals.csv")
    drift_path = os.path.join(LOG_DIR, "drift_log.csv")

    if not os.path.exists(predictions_path):
        raise FileNotFoundError(f"Missing predictions.csv → {predictions_path}")

    if not os.path.exists(actuals_path):
        raise FileNotFoundError(f"Missing actuals.csv → {actuals_path}")

    predictions = pd.read_csv(predictions_path)
    actuals = pd.read_csv(actuals_path)

    # merge actual + predicted safely
    if "store_id" in predictions.columns and "item_id" in predictions.columns:
        df = pd.merge(actuals, predictions, on=["store_id", "item_id"], how="inner")
    else:
        df = pd.DataFrame({
            "actual": actuals["actual"],
            "predicted": predictions["predicted"]
        })

    drift_df = None
    if os.path.exists(drift_path):
        drift_df = pd.read_csv(drift_path)

    return df, drift_df


# -------------------------------------------------
# 1. ACTUAL VS PREDICTED
# -------------------------------------------------
def plot_actual_vs_predicted(df):
    print("Generating Actual vs Predicted...")

    plt.figure(figsize=(12, 6))
    plt.plot(df["actual"].values, label="Actual")
    plt.plot(df["predicted"].values, label="Predicted")

    plt.title("Actual vs Predicted Grocery Demand")
    plt.xlabel("Samples")
    plt.ylabel("Demand")
    plt.legend()
    plt.grid()

    path = os.path.join(OUTPUT_DIR, "actual_vs_predicted.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()

    print("Saved:", path)


# -------------------------------------------------
# 2. ERROR DISTRIBUTION
# -------------------------------------------------
def plot_error_distribution(df):
    print("Generating Error Distribution...")

    df["error"] = df["actual"] - df["predicted"]

    plt.figure(figsize=(10, 5))
    sns.histplot(df["error"], bins=30, kde=True)

    plt.title("Prediction Error Distribution")

    path = os.path.join(OUTPUT_DIR, "error_distribution.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()

    print("Saved:", path)


# -------------------------------------------------
# 3. STORE WISE
# -------------------------------------------------
def plot_store_wise(df):
    if "store_id" not in df.columns:
        return

    print("Generating Store-wise plot...")

    store_summary = df.groupby("store_id")[["actual", "predicted"]].mean()

    store_summary.plot(kind="bar", figsize=(10, 6))

    plt.title("Store-wise Demand Comparison")
    plt.ylabel("Demand")

    path = os.path.join(OUTPUT_DIR, "store_wise.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()

    print("Saved:", path)


# -------------------------------------------------
# 4. ITEM WISE
# -------------------------------------------------
def plot_item_wise(df):
    if "item_id" not in df.columns:
        return

    print("Generating Item-wise plot...")

    item_summary = df.groupby("item_id")[["actual", "predicted"]].mean().head(10)

    item_summary.plot(kind="bar", figsize=(10, 6))

    plt.title("Top Item Demand Comparison")
    plt.ylabel("Demand")

    path = os.path.join(OUTPUT_DIR, "item_wise.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()

    print("Saved:", path)


# -------------------------------------------------
# 5. DRIFT PLOT
# -------------------------------------------------
def plot_drift(drift_df):
    if drift_df is None:
        print("No drift file found — skipping drift plots")
        return

    print("Generating Drift plot...")

    plt.figure(figsize=(10, 5))
    plt.plot(drift_df["rolling_rmse"], marker="o")

    plt.title("Model Drift (Rolling RMSE)")
    plt.xlabel("Week")
    plt.ylabel("RMSE")
    plt.grid()

    path = os.path.join(OUTPUT_DIR, "drift_rmse.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()

    print("Saved:", path)


# -------------------------------------------------
# 6. DRIFT THRESHOLD
# -------------------------------------------------
def plot_drift_threshold(drift_df, threshold=14):
    if drift_df is None:
        return

    print("Generating Drift Threshold plot...")

    plt.figure(figsize=(10, 5))
    plt.plot(drift_df["rolling_rmse"], label="RMSE")
    plt.axhline(y=threshold, color="r", linestyle="--", label="Threshold")

    plt.title("Drift Detection with Threshold")
    plt.legend()
    plt.grid()

    path = os.path.join(OUTPUT_DIR, "drift_threshold.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()

    print("Saved:", path)


# -------------------------------------------------
# MAIN EXECUTION
# -------------------------------------------------
def main():
    print("\nLoading data...\n")

    df, drift_df = load_data()

    print("\nGenerating visualizations...\n")

    plot_actual_vs_predicted(df)
    plot_error_distribution(df)
    plot_store_wise(df)
    plot_item_wise(df)
    plot_drift(drift_df)
    plot_drift_threshold(drift_df)

    print("\nALL VISUALIZATIONS COMPLETED ✔")
    print("Check outputs/ folder")


# -------------------------------------------------
# RUN SCRIPT
# -------------------------------------------------
if __name__ == "__main__":
    main()