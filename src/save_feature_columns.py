import pandas as pd
import json

df = pd.read_csv("data/processed/grocery_features.csv")

X = df.drop(columns=["sales_units", "date"])

feature_columns = X.columns.tolist()

import os
os.makedirs("models", exist_ok=True)

with open("models/feature_columns.json", "w") as f:
    json.dump(feature_columns, f)

print("Saved feature columns:", len(feature_columns))