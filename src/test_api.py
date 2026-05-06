#!/usr/bin/env python3

import requests
import json
import time
from datetime import datetime
import os

API_URL = "http://localhost:8000"

SINGLE_URL = f"{API_URL}/predict"
FESTIVAL_URL = f"{API_URL}/predict/festival"


# =========================
# TEST DATA (SINGLE)
# =========================
single_test_cases = [
    {
        "name": "Fresh Vegetables - Normal Day",
        "data": {
            "item_name": "tomato",
            "category": "vegetables",
            "store_id": 1,
            "current_stock": 120,
            "is_festival": False,
            "festival_name": "none",
            "has_discount": False,
            "discount_pct": 0,
            "has_promotion": False,
            "promotion": 0
        }
    },
    {
        "name": "Dairy Product - High Demand",
        "data": {
            "item_name": "milk",
            "category": "dairy",
            "store_id": 2,
            "current_stock": 50,
            "is_festival": False,
            "festival_name": "none",
            "has_discount": True,
            "discount_pct": 10,
            "has_promotion": True,
            "promotion": 1
        }
    },
    {
        "name": "Snacks - Weekend Effect",
        "data": {
            "item_name": "chips",
            "category": "snacks",
            "store_id": 3,
            "current_stock": 200,
            "is_festival": False,
            "festival_name": "none",
            "has_discount": True,
            "discount_pct": 5,
            "has_promotion": False,
            "promotion": 0
        }
    },
    {
        "name": "High Price Item",
        "data": {
            "item_name": "almonds",
            "category": "dry_fruits",
            "store_id": 4,
            "current_stock": 80,
            "is_festival": False,
            "festival_name": "none",
            "has_discount": False,
            "discount_pct": 0,
            "has_promotion": False,
            "promotion": 0
        }
    },
    {
        "name": "Low Stock Scenario",
        "data": {
            "item_name": "rice",
            "category": "grains",
            "store_id": 1,
            "current_stock": 10,
            "is_festival": False,
            "festival_name": "none",
            "has_discount": True,
            "discount_pct": 20,
            "has_promotion": True,
            "promotion": 2
        }
    },
    {
        "name": "High Promotion Case",
        "data": {
            "item_name": "soft_drink",
            "category": "beverages",
            "store_id": 2,
            "current_stock": 150,
            "is_festival": False,
            "festival_name": "none",
            "has_discount": True,
            "discount_pct": 40,
            "has_promotion": True,
            "promotion": 3
        }
    }
]


# =========================
# TEST DATA (FESTIVAL)
# =========================
festival_test_cases = [
    {
        "name": "New Year Festival",
        "data": {
            "festival_name": "new year",
            "store_id": 1,
            "top_n": 5,
            "has_discount": True,
            "discount_pct": 15,
            "has_promotion": True,
            "promotion": 1
        }
    },
    {
        "name": "Diwali Demand Surge",
        "data": {
            "festival_name": "diwali",
            "store_id": 2,
            "top_n": 6,
            "has_discount": True,
            "discount_pct": 25,
            "has_promotion": True,
            "promotion": 2
        }
    },
    {
        "name": "Christmas Festival",
        "data": {
            "festival_name": "christmas",
            "store_id": 3,
            "top_n": 5,
            "has_discount": True,
            "discount_pct": 20,
            "has_promotion": True,
            "promotion": 1
        }
    },
    {
        "name": "Pongal Festival (South India)",
        "data": {
            "festival_name": "pongal",
            "store_id": 4,
            "top_n": 5,
            "has_discount": False,
            "discount_pct": 0,
            "has_promotion": True,
            "promotion": 1
        }
    }
]


# =========================
# HELPERS
# =========================
def print_line(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


# =========================
# SINGLE PREDICTION TEST
# =========================
def test_single():
    print_line("🟢 SINGLE PREDICTION TEST")

    for test in single_test_cases:
        print(f"\n▶ {test['name']}")

        res = requests.post(SINGLE_URL, json=test["data"])
        data = res.json()

        print("Response:", json.dumps(data, indent=2))

        # simulate triggering actual generation
        os.system("python mlops/generate_actuals.py")


# =========================
# FESTIVAL PREDICTION TEST
# =========================
def test_festival():
    print_line("🟣 FESTIVAL PREDICTION TEST")

    for test in festival_test_cases:
        print(f"\n▶ {test['name']}")

        res = requests.post(FESTIVAL_URL, json=test["data"])
        data = res.json()

        print("Response:", json.dumps(data, indent=2))

        # simulate triggering actual generation
        os.system("python mlops/generate_actuals.py")


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    print_line("🚀 MLOps TEST SUITE STARTED")

    test_single()
    time.sleep(1)
    test_festival()

    print_line("✅ ALL TESTS COMPLETED")