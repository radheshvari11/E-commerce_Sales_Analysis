"""
eda_analysis.py
Exploratory Data Analysis for the E-Commerce Sales dataset.
Run this script to see all insights printed to the terminal.
"""

import os
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from generate_data import generate_ecommerce_data

# ── Setup ─────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", palette="muted")
os.makedirs("outputs", exist_ok=True)

# ── 1. Load / generate data ───────────────────────────────────
print("=" * 55)
print("  E-COMMERCE SALES – EXPLORATORY DATA ANALYSIS")
print("=" * 55)

if not os.path.exists("data/orders.csv"):
    generate_ecommerce_data()

customers   = pd.read_csv("data/customers.csv",   parse_dates=["join_date"])
products    = pd.read_csv("data/products.csv")
orders      = pd.read_csv("data/orders.csv",      parse_dates=["order_date"])
order_items = pd.read_csv("data/order_items.csv")

# Flat master table
df = (order_items
      .merge(orders[["order_id", "customer_id", "order_date", "status"]], on="order_id")
      .merge(customers[["customer_id", "state", "city"]], on="customer_id"))

delivered = df[df["status"] == "Delivered"]

# ── 2. Dataset overview ───────────────────────────────────────
print("\n📋 DATASET OVERVIEW")
print(f"  Customers   : {customers.shape[0]:,}")
print(f"  Products    : {products.shape[0]:,}")
print(f"  Orders      : {orders.shape[0]:,}")
print(f"  Order Items : {order_items.shape[0]:,}")
print(f"  Date Range  : {orders['order_date'].min().date()} → {orders['order_date'].max().date()}")

# ── 3. Missing values check ───────────────────────────────────
print("\n🔍 MISSING VALUES")
for name, frame in [("customers", customers), ("products", products),
                    ("orders", orders), ("order_items", order_items)]:
    missing = frame.isnull().sum().sum()
    print(f"  {name:15s}: {missing} missing values")

# ── 4. KPIs ───────────────────────────────────────────────────
total_revenue = delivered["total_price"].sum()
total_orders  = orders["order_id"].nunique()
aov           = delivered.groupby("order_id")["total_price"].sum().mean()

print("\n💰 KEY BUSINESS METRICS")
print(f"  Total Revenue      : ${total_revenue:,.2f}")
print(f"  Total Orders       : {total_orders:,}")
print(f"  Avg Order Value    : ${aov:,.2f}")
print(f"  Unique Customers   : {customers.shape[0]:,}")
print(f"  Unique Products    : {products.shape[0]:,}")

# ── 5. Revenue by category ────────────────────────────────────
print("\n🏷️  REVENUE BY CATEGORY")
cat_rev = (delivered.groupby("category")["total_price"]
           .sum().sort_values(ascending=False).reset_index())
cat_rev.columns = ["Category", "Revenue"]
cat_rev["Revenue %"] = (cat_rev["Revenue"] / cat_rev["Revenue"].sum() * 100).round(2)
print(cat_rev.to_string(index=False))

# ── 6. Order status breakdown ─────────────────────────────────
print("\n📦 ORDER STATUS BREAKDOWN")
status = (orders.groupby("status")["order_id"]
          .count().sort_values(ascending=False).reset_index())
status.columns = ["Status", "Count"]
status["Pct"] = (status["Count"] / status["Count"].sum() * 100).round(2)
print(status.to_string(index=False))

# ── 7. Top 5 products ─────────────────────────────────────────
print("\n🏆 TOP 5 PRODUCTS BY REVENUE")
top5 = (delivered.groupby(["product_name", "category"])["total_price"]
        .sum().nlargest(5).reset_index())
top5.columns = ["Product", "Category", "Revenue"]
print(top5.to_string(index=False))

# ── 8. Revenue by state ───────────────────────────────────────
print("\n🗺️  REVENUE BY STATE (Top 5)")
state_rev = (delivered.groupby("state")["total_price"]
             .sum().nlargest(5).reset_index())
state_rev.columns = ["State", "Revenue"]
print(state_rev.to_string(index=False))

# ── 9. SQL queries via sqlite3 ────────────────────────────────
print("\n🗃️  RUNNING SQL QUERIES ON SQLITE DATABASE...")
conn = sqlite3.connect(":memory:")
customers.to_sql("customers",   conn, index=False, if_exists="replace")
products.to_sql("products",     conn, index=False, if_exists="replace")
orders.to_sql("orders",         conn, index=False, if_exists="replace")
order_items.to_sql("order_items", conn, index=False, if_exists="replace")

sql_yoy = """
SELECT strftime('%Y', o.order_date) AS year,
       ROUND(SUM(oi.total_price), 2) AS revenue,
       COUNT(DISTINCT o.order_id)    AS orders
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'Delivered'
GROUP BY year ORDER BY year;
"""
yoy = pd.read_sql(sql_yoy, conn)
print("\n  Year-over-Year Revenue:")
print(yoy.to_string(index=False))
conn.close()

# ── 10. Plots ─────────────────────────────────────────────────
print("\n📊 SAVING CHARTS TO outputs/ folder...")

# Monthly revenue line chart
delivered_copy = delivered.copy()
delivered_copy["month"] = delivered_copy["order_date"].dt.to_period("M").astype(str)
monthly = delivered_copy.groupby("month")["total_price"].sum()

fig, ax = plt.subplots(figsize=(12, 4))
monthly.plot(ax=ax, marker="o", color="#636EFA")
ax.set_title("Monthly Revenue (Delivered Orders)", fontsize=14)
ax.set_xlabel("Month"); ax.set_ylabel("Revenue ($)")
plt.xticks(rotation=45, ha="right"); plt.tight_layout()
plt.savefig("outputs/monthly_revenue.png", dpi=150)
plt.close()

# Category revenue bar chart
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(data=cat_rev, x="Revenue", y="Category", palette="Blues_r", ax=ax)
ax.set_title("Revenue by Category", fontsize=14)
plt.tight_layout()
plt.savefig("outputs/category_revenue.png", dpi=150)
plt.close()

# Order status pie
fig, ax = plt.subplots(figsize=(6, 6))
status.set_index("Status")["Count"].plot.pie(autopct="%1.1f%%", ax=ax, startangle=140)
ax.set_title("Order Status Distribution"); ax.set_ylabel("")
plt.tight_layout()
plt.savefig("outputs/order_status.png", dpi=150)
plt.close()

print("  ✅ Charts saved: monthly_revenue.png, category_revenue.png, order_status.png")
print("\n✅ EDA complete!\n")
