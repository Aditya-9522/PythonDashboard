# data_load_example.py
import pandas as pd
from sqlalchemy import create_engine

# read sales csv
sales = pd.read_csv("data/sales.csv", parse_dates=["date"])

# read customers from sqlite
engine = create_engine("sqlite:///data/customers.db")
customers = pd.read_sql("customers", engine, parse_dates=["signup_date"])

# join to get region/name on sales
df = sales.merge(customers, on="customer_id", how="left")
# some simple derived columns
df["month"] = df["date"].dt.to_period("M").astype(str)
df["amount"] = df["amount"].astype(float)

print(df.head())
