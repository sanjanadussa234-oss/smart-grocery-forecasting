# src/feature_engineering.py

import pandas as pd
import os
import joblib
from sklearn.preprocessing import LabelEncoder

# -------------------------
# Paths
# -------------------------
INPUT_PATH = "data/new_processed/cleaned_data.csv"
FEATURED_DIR = "data/new_featured/"

OUTPUT_PATH = FEATURED_DIR + "featured_data.csv"

ITEM_ENCODER_PATH = FEATURED_DIR + "item_encoder.pkl"
CATEGORY_ENCODER_PATH = FEATURED_DIR + "category_encoder.pkl"
FESTIVAL_ENCODER_PATH = FEATURED_DIR + "festival_encoder.pkl"

os.makedirs(FEATURED_DIR, exist_ok=True)


def feature_engineering():
    print("Loading cleaned data...")
    df = pd.read_csv(INPUT_PATH)

    print("Applying feature engineering...")

    # -------------------------
    # Convert date
    # -------------------------
    df['date'] = pd.to_datetime(df['date'])

    # -------------------------
    # Encoding categorical variables
    # -------------------------
    le_item = LabelEncoder()
    df['item_encoded'] = le_item.fit_transform(df['item_id'])

    le_category = LabelEncoder()
    df['category_encoded'] = le_category.fit_transform(df['category'])

    le_festival = LabelEncoder()
    df['festival_encoded'] = le_festival.fit_transform(df['festival'])

    # Save encoders
    joblib.dump(le_item, ITEM_ENCODER_PATH)
    joblib.dump(le_category, CATEGORY_ENCODER_PATH)
    joblib.dump(le_festival, FESTIVAL_ENCODER_PATH)

    # -------------------------
    # Time features
    # -------------------------
    df['day'] = df['date'].dt.day
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    df['weekofyear'] = df['date'].dt.isocalendar().week.astype(int)

    # -------------------------
    # Sort for lag features
    # -------------------------
    df = df.sort_values(by=['store_id', 'item_id', 'date'])

    # -------------------------
    # Lag features
    # -------------------------
    df['lag_1'] = df.groupby(['store_id', 'item_id'])['sales_units'].shift(1)
    df['lag_7'] = df.groupby(['store_id', 'item_id'])['sales_units'].shift(7)

    # -------------------------
    # Rolling mean feature
    # -------------------------
    df['rolling_mean_7'] = df.groupby(['store_id', 'item_id'])['sales_units'] \
                            .transform(lambda x: x.rolling(7).mean())

    # -------------------------
    # Handle missing values
    # -------------------------
    df.fillna(0, inplace=True)

    # -------------------------
    # Select only model features
    # -------------------------
    FEATURE_COLUMNS = [
        'store_id',
        'item_encoded',
        'category_encoded',
        'festival_encoded',
        'price',
        'base_price',
        'discount_pct',
        'promotion',
        'day_of_week',
        'month',
        'weekofyear',
        'lag_1',
        'lag_7',
        'rolling_mean_7',
        'temperature_c',
        'rainfall_mm',
        'humidity_pct'
    ]

    TARGET = 'sales_units'

    df_model = df[FEATURE_COLUMNS + [TARGET]]

    # -------------------------
    # Debug: Check final columns
    # -------------------------
    print("Final columns used for model:")
    print(df_model.columns)

    # -------------------------
    # Save final dataset
    # -------------------------
    df_model.to_csv(OUTPUT_PATH, index=False)

    print("✅ Feature engineering complete.")
    print(f"Saved featured data → {OUTPUT_PATH}")
    print("Encoders saved in data/new_featured/")


if __name__ == "__main__":
    feature_engineering()