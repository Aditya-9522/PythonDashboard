# generate_data.py
import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine

np.random.seed(42)

os.makedirs("data", exist_ok=True)

# --- sales.csv ---
n_rows = 1200
dates = pd.date_range("2024-01-01", periods=180, freq="D")
categories = ["Electronics", "Clothing", "Home", "Books"]
regions = ["North", "South", "East", "West"]

sales = pd.DataFrame({
    "date": np.random.choice(dates, n_rows),
    "category": np.random.choice(categories, n_rows, p=[0.25, 0.35, 0.25, 0.15]),
    "region": np.random.choice(regions, n_rows),
    "customer_id": np.random.randint(1, 301, n_rows)
})
# amount depends on category with noise
base = {"Electronics": 120, "Clothing": 45, "Home": 75, "Books": 20}
sales["amount"] = sales["category"].map(base) * (1 + np.random.normal(0, 0.25, n_rows))
sales["amount"] = sales["amount"].round(2)
sales = sales.sort_values("date").reset_index(drop=True)
sales.to_csv("data/sales.csv", index=False)
print("Wrote data/sales.csv")

# --- customers table in SQLite ---
n_customers = 300
customer_df = pd.DataFrame({
    "customer_id": range(1, n_customers + 1),
    "name": [f"Customer_{i}" for i in range(1, n_customers + 1)],
    "signup_date": pd.to_datetime("2022-01-01") + pd.to_timedelta(np.random.randint(0, 700, n_customers), unit='D'),
    "region": np.random.choice(regions, n_customers)
})
# write to SQLite
engine = create_engine("sqlite:///data/customers.db")
customer_df.to_sql("customers", engine, index=False, if_exists="replace")
print("Wrote data/customers.db (table: customers)")

