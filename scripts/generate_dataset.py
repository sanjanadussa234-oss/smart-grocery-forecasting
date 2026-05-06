# scripts/generate_dataset.py
"""
Generate large synthetic dataset with realistic characteristics
Including: 8 stores, multiple items, seasonal patterns, festivals, weather, and promotions
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================
# CONFIGURATION
# ============================================
DATA_DIR = Path(__file__).parent.parent / "data" / "raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)

STORES = [f"S{str(i).zfill(2)}" for i in range(1, 9)]  # S01 to S08
ITEMS = [f"I{str(i).zfill(3)}" for i in range(1, 101)]  # I001 to I100

CATEGORIES = {
    "Vegetables": list(range(0, 20)),
    "Fruits": list(range(20, 35)),
    "Dairy": list(range(35, 50)),
    "Beverages": list(range(50, 65)),
    "Grains": list(range(65, 80)),
    "Pulses": list(range(80, 90)),
    "Snacks": list(range(90, 100)),
}

ITEM_NAMES = {
    "Vegetables": ["Tomato", "Potato", "Onion", "Spinach", "Carrot", "Cabbage", "Cucumber", "Pepper", "Broccoli", "Cauliflower",
                   "Peas", "Beans", "Radish", "Beet", "Squash", "Zucchini", "Eggplant", "Lettuce", "Kale", "Parsnip"],
    "Fruits": ["Apple", "Banana", "Orange", "Mango", "Strawberry", "Grapes", "Watermelon", "Papaya", "Pineapple", "Guava",
               "Pomegranate", "Coconut", "Lemon", "Lime", "Kiwi"],
    "Dairy": ["Milk", "Yogurt", "Cheese", "Butter", "Cream", "Ghee", "Paneer", "Curd", "Milk Powder", "Ice Cream",
              "Condensed Milk", "Whey", "Lactose Free Milk", "Flavored Yogurt", "Mozzarella"],
    "Beverages": ["Water", "Coffee", "Tea", "Juice", "Soft Drink", "Energy Drink", "Sports Drink", "Milk Shake", "Lassi", "Smoothie",
                  "Herbal Tea", "Coconut Water", "Lemonade", "Buttermilk", "Beer"],
    "Grains": ["Rice", "Wheat", "Flour", "Oats", "Corn", "Barley", "Millet", "Quinoa", "Basmati", "Brown Rice",
               "Rye", "Buckwheat", "Sorghum", "Lentil Flour", "Chickpea Flour"],
    "Pulses": ["Dal", "Lentils", "Chickpeas", "Kidney Beans", "Black Beans", "Peas", "Soybeans", "Peanuts", "Chick Pea", "Red Beans"],
    "Snacks": ["Chips", "Biscuits", "Cookies", "Popcorn", "Nuts", "Dried Fruit", "Granola", "Cereal", "Crackers", "Pretzels"],
}

# ============================================
# HELPER FUNCTIONS
# ============================================
def get_item_name_and_category(item_idx):
    """Get item name and category based on item index"""
    for category, item_indices in CATEGORIES.items():
        if item_idx in item_indices:
            local_idx = item_indices.index(item_idx)
            item_name = ITEM_NAMES[category][local_idx % len(ITEM_NAMES[category])]
            return item_name, category
    return f"Item_{item_idx}", "Other"

def get_seasonal_multiplier(month):
    """Get demand multiplier based on season"""
    if month in [12, 1, 2]:  # Winter
        return {"Vegetables": 1.2, "Fruits": 0.8, "Beverages": 1.0, "Dairy": 1.3, "Snacks": 1.4}
    elif month in [3, 4, 5]:  # Summer
        return {"Vegetables": 0.9, "Fruits": 1.5, "Beverages": 1.6, "Dairy": 1.1, "Snacks": 1.2}
    elif month in [6, 7, 8, 9]:  # Monsoon
        return {"Vegetables": 1.3, "Fruits": 1.0, "Beverages": 1.2, "Dairy": 1.0, "Snacks": 1.1}
    else:  # Autumn
        return {"Vegetables": 1.1, "Fruits": 1.2, "Beverages": 1.0, "Dairy": 1.1, "Snacks": 1.3}

def get_festival_flag(date):
    """Determine if date is during a festival"""
    festivals = {
        (1, 1): ("New Year", 1),
        (3, 7): ("Holi", 1),  # 2023
        (5, 3): ("Eid", 1),
        (8, 15): ("Independence Day", 1),
        (10, 1): ("Navratri", 1),
        (10, 24): ("Diwali", 1),  # 2022
        (12, 25): ("Christmas", 1),
    }
    
    month_day = (date.month, date.day)
    for (m, d), (name, flag) in festivals.items():
        if date.month == m and abs(date.day - d) <= 5:
            return flag, name
    return 0, "None"

def generate_sales_data():
    """Generate synthetic grocery sales data"""
    logger.info("🔄 Generating synthetic dataset...")
    
    data = []
    
    # Date range: 2 years of data
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    current_date = start_date
    dates = []
    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)
    
    logger.info(f"📅 Date range: {start_date.date()} to {end_date.date()}")
    logger.info(f"📊 Total days: {len(dates)}")
    
    # Generate data for each store-item combination
    total_rows = len(STORES) * len(ITEMS) * len(dates)
    logger.info(f"📦 Generating {total_rows:,} total rows...")
    
    counter = 0
    for store_id in STORES:
        for item_idx, item_id in enumerate(ITEMS):
            
            # Get item properties
            item_name, category = get_item_name_and_category(item_idx)
            
            # Base demand for this store-item
            base_demand = np.random.uniform(30, 150)
            
            # Price properties
            base_price = np.random.uniform(20, 500)
            price_variation = np.random.uniform(0, 0.3)  # Up to 30% variation
            
            for date in dates:
                # Day properties
                day_of_week = date.weekday()  # 0=Monday, 6=Sunday
                month = date.month
                year = date.year
                weekend = 1 if day_of_week >= 5 else 0
                
                # Season
                if month in [12, 1, 2]:
                    season = "Winter"
                elif month in [3, 4, 5]:
                    season = "Summer"
                elif month in [6, 7, 8, 9]:
                    season = "Monsoon"
                else:
                    season = "Autumn"
                
                # Festival
                festival_flag, festival_name = get_festival_flag(date)
                
                # Weather (realistic patterns)
                if season == "Summer":
                    temp = np.random.normal(35, 5)
                    rainfall = np.random.exponential(1)
                    humidity = np.random.normal(60, 15)
                elif season == "Monsoon":
                    temp = np.random.normal(28, 3)
                    rainfall = np.random.exponential(10)
                    humidity = np.random.normal(75, 10)
                elif season == "Winter":
                    temp = np.random.normal(20, 3)
                    rainfall = np.random.exponential(2)
                    humidity = np.random.normal(55, 10)
                else:  # Autumn
                    temp = np.random.normal(25, 3)
                    rainfall = np.random.exponential(3)
                    humidity = np.random.normal(65, 10)
                
                temp = np.clip(temp, -5, 50)
                rainfall = np.clip(rainfall, 0, 100)
                humidity = np.clip(humidity, 20, 95)
                
                # Promotion (20% chance of promotion)
                if np.random.random() < 0.2:
                    promotion = np.random.randint(1, 4)
                    discount_pct = np.random.uniform(5, 40)
                else:
                    promotion = 0
                    discount_pct = 0.0
                
                # Price with variation
                current_price = base_price * (1 + np.random.uniform(-price_variation, price_variation))
                if discount_pct > 0:
                    current_price = current_price * (1 - discount_pct / 100)
                
                # Sales demand (realistic with patterns)
                seasonal_mult = get_seasonal_multiplier(month).get(category, 1.0)
                festival_mult = 2.0 if festival_flag == 1 else 1.0
                weekend_mult = 1.2 if weekend == 1 else 1.0
                promo_mult = 1.5 if promotion > 0 else 1.0
                
                # Random noise
                noise = np.random.normal(1, 0.15)
                
                sales_units = int(base_demand * seasonal_mult * festival_mult * weekend_mult * promo_mult * noise)
                sales_units = np.clip(sales_units, 0, 500)
                
                # Append row
                data.append({
                    "date": date.date(),
                    "store_id": store_id,
                    "item_id": item_id,
                    "item_name": item_name,
                    "category": category,
                    "sales_units": sales_units,
                    "price": round(current_price, 2),
                    "base_price": round(base_price, 2),
                    "discount_pct": round(discount_pct, 1),
                    "promotion": promotion,
                    "day_of_week": day_of_week,
                    "day_name": date.strftime("%A"),
                    "month": month,
                    "year": year,
                    "weekend": weekend,
                    "season": season,
                    "festival": festival_name,
                    "festival_flag": festival_flag,
                    "temperature_c": round(temp, 1),
                    "rainfall_mm": round(rainfall, 1),
                    "humidity_pct": round(humidity, 1),
                })
                
                counter += 1
                if counter % 100000 == 0:
                    logger.info(f"⏳ Generated {counter:,} rows...")
    
    logger.info(f"✅ Generated {len(data):,} rows")
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    logger.info(f"📊 Dataset shape: {df.shape}")
    logger.info(f"📅 Date range: {df['date'].min()} to {df['date'].max()}")
    logger.info(f"🏪 Stores: {df['store_id'].nunique()}")
    logger.info(f"📦 Items: {df['item_id'].nunique()}")
    logger.info(f"🎉 Festivals: {df[df['festival_flag']==1].shape[0]} rows with festivals")
    
    return df

# ============================================
# MAIN EXECUTION
# ============================================
if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("🛒 GENERATING LARGE SYNTHETIC GROCERY DATASET")
    logger.info("=" * 70)
    
    # Generate dataset
    df = generate_sales_data()
    
    # Save dataset
    output_file = DATA_DIR / "grocery_data.csv"
    logger.info(f"💾 Saving dataset to {output_file}...")
    df.to_csv(output_file, index=False)
    logger.info(f"✅ Dataset saved successfully!")
    
    # Dataset statistics
    logger.info("\n📊 DATASET STATISTICS:")
    logger.info(f"Total Rows: {len(df):,}")
    logger.info(f"Total Columns: {len(df.columns)}")
    logger.info(f"Date Range: {df['date'].min()} to {df['date'].max()}")
    logger.info(f"Stores: {df['store_id'].unique().tolist()}")
    logger.info(f"Items: {df['item_id'].nunique()}")
    logger.info(f"Categories: {df['category'].unique().tolist()}")
    logger.info(f"Avg Sales Units: {df['sales_units'].mean():.2f}")
    logger.info(f"Promotion Rate: {(df['promotion'] > 0).sum() / len(df) * 100:.2f}%")
    logger.info(f"Festival Days: {(df['festival_flag'] == 1).sum():,}")
    
    logger.info("\n✅ DATASET READY FOR PREPROCESSING!")
    logger.info("=" * 70)