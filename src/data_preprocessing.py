# src/preprocess.py

import pandas as pd
import os

# Paths
RAW_PATH = "data/raw/grocery_data.csv"
PROCESSED_DIR = "data/new_processed/"
CLEANED_PATH = PROCESSED_DIR + "cleaned_data.csv"
MAPPING_PATH = PROCESSED_DIR + "item_mapping.csv"

os.makedirs(PROCESSED_DIR, exist_ok=True)


def preprocess():
    print("Loading raw data...")
    df = pd.read_csv(RAW_PATH)

    print("Cleaning data...")

    # Convert date
    df['date'] = pd.to_datetime(df['date'])

    # Handle missing values
    df['festival'] = df['festival'].fillna("None")

    # Standardize text
    df['item_name'] = df['item_name'].str.lower()
    df['category'] = df['category'].str.lower()
    df['festival'] = df['festival'].str.lower()

    # Convert store_id (S01 → 1)
    df['store_id'] = df['store_id'].str.replace('S', '').astype(int)

    # Create item mapping
    print("Creating item mapping...")
    item_mapping = df[['item_id', 'item_name', 'category']].drop_duplicates()

    # Save outputs
    df.to_csv(CLEANED_PATH, index=False)
    item_mapping.to_csv(MAPPING_PATH, index=False)

    print("✅ Preprocessing complete.")
    print(f"Saved cleaned data → {CLEANED_PATH}")
    print(f"Saved item mapping → {MAPPING_PATH}")


if __name__ == "__main__":
    preprocess()