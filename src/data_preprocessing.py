# src/data_preprocessing.py

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

def preprocess_data(path):
    print("📥 Loading dataset...")

    df = pd.read_csv(path)

    # -------------------------------
    # 1. FIX DATE COLUMN
    # -------------------------------
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # -------------------------------
    # 2. SORT DATA (VERY IMPORTANT)
    # -------------------------------
    df = df.sort_values(["store_id", "item_id", "date"]).reset_index(drop=True)

    print("Initial Shape:", df.shape)

    # -------------------------------
    # 3. HANDLE MISSING VALUES
    # -------------------------------

    # Target variable
    df["sales_units"] = df["sales_units"].fillna(0)

    # Price columns
    df["price"] = df.groupby(["store_id", "item_id"])["price"].ffill().bfill()
    df["base_price"] = df.groupby(["store_id", "item_id"])["base_price"].ffill().bfill()

    # Promotion
    if "promotion" in df.columns:
        df["promotion"] = df["promotion"].fillna(0).astype(int)
    else:
        df["promotion"] = 0

    # Discount
    df["discount_pct"] = df["discount_pct"].fillna(0)

    # Weather
    if "temperature_c" in df.columns:
        df["temperature_c"] = df["temperature_c"].interpolate()
    if "humidity_pct" in df.columns:
        df["humidity_pct"] = df["humidity_pct"].interpolate()
    if "rainfall_mm" in df.columns:
        df["rainfall_mm"] = df["rainfall_mm"].fillna(0)

    # Festival
    if "festival_flag" in df.columns:
        df["festival_flag"] = df["festival_flag"].fillna(0)
    else:
        df["festival_flag"] = 0

    # Weekend
    if "weekend" in df.columns:
        df["weekend"] = df["weekend"].fillna(0)

    # -------------------------------
    # 4. ENCODING (CRITICAL)
    # -------------------------------

    le_store = LabelEncoder()
    le_item = LabelEncoder()

    df["store_id_enc"] = le_store.fit_transform(df["store_id"].astype(str))
    df["item_id_enc"] = le_item.fit_transform(df["item_id"].astype(str))

    # Season encoding (safe mapping)
    season_map = {
        "Winter": 0,
        "Summer": 1,
        "Monsoon": 2,
        "Autumn": 3
    }
    df["season_enc"] = df["season"].map(season_map).fillna(0)

    # Category encoding (one-hot)
    if "category" in df.columns:
        df = pd.get_dummies(df, columns=["category"], drop_first=False)

    # -------------------------------
    # 5. DROP STRING COLUMNS
    # -------------------------------
    drop_cols = [
        "store_id",
        "item_id",
        "item_name",
        "season",
        "festival",
        "day_name"
    ]

    df = df.drop(columns=[col for col in drop_cols if col in df.columns])

    # -------------------------------
    # 6. FINAL CHECK
    # -------------------------------
    print("\nFinal Shape:", df.shape)
    print("\nData Types:\n", df.dtypes)

    # Ensure no object columns remain
    object_cols = df.select_dtypes(include=["object"]).columns
    if len(object_cols) > 0:
        print("\n⚠️ Warning: Object columns still present:", object_cols)
    else:
        print("\n✅ No object columns remaining")

    return df


if __name__ == "__main__":
    df = preprocess_data("data/raw/grocery_data.csv")

    df.to_csv("data/processed/grocery_clean.csv", index=False)

    print("\n✅ Preprocessing Completed Successfully!")