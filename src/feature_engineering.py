# src/feature_engineering.py

import pandas as pd
import numpy as np


def create_features(path):
    print("📥 Loading processed dataset...")

    df = pd.read_csv(path, parse_dates=["date"])

    # -----------------------------------
    # 1. SORT DATA (VERY IMPORTANT)
    # -----------------------------------
    df = df.sort_values(["store_id_enc", "item_id_enc", "date"]).reset_index(drop=True)

    # -----------------------------------
    # 2. LAG FEATURES
    # -----------------------------------
    print("⚙️ Creating lag features...")

    df["lag_1"] = df.groupby(["store_id_enc", "item_id_enc"])["sales_units"].shift(1)
    df["lag_7"] = df.groupby(["store_id_enc", "item_id_enc"])["sales_units"].shift(7)
    df["lag_14"] = df.groupby(["store_id_enc", "item_id_enc"])["sales_units"].shift(14)

    # -----------------------------------
    # 3. ROLLING FEATURES
    # -----------------------------------
    print("📈 Creating rolling features...")

    df["rolling_mean_7"] = df.groupby(["store_id_enc", "item_id_enc"])["sales_units"] \
        .transform(lambda x: x.shift(1).rolling(window=7).mean())

    df["rolling_std_7"] = df.groupby(["store_id_enc", "item_id_enc"])["sales_units"] \
        .transform(lambda x: x.shift(1).rolling(window=7).std())

    # -----------------------------------
    # 4. PRICE FEATURES
    # -----------------------------------
    print("💰 Creating price features...")

    df["price_diff"] = df["base_price"] - df["price"]
    df["price_ratio"] = df["price"] / (df["base_price"] + 1e-5)

    # -----------------------------------
    # 5. PROMOTION EFFECT
    # -----------------------------------
    df["promo_effect"] = df["promotion"] * df["discount_pct"]

    # -----------------------------------
    # 6. CYCLICAL FEATURES (FIXED)
    # -----------------------------------
    print("📅 Creating seasonal features...")

    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)

    df["dow_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7)
    df["dow_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7)

    # -----------------------------------
    # 7. DROP NaN ROWS (FROM LAGS)
    # -----------------------------------
    print("🧹 Dropping NaN rows...")

    df = df.dropna().reset_index(drop=True)

    # -----------------------------------
    # FINAL INFO
    # -----------------------------------
    print("\nFinal Shape after feature engineering:", df.shape)
    print("\nSample Data:\n", df.head())

    return df


if __name__ == "__main__":
    df = create_features("data/processed/grocery_clean.csv")

    df.to_csv("data/processed/grocery_features.csv", index=False)

    print("\n✅ Feature Engineering Completed Successfully!")