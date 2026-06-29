"""
generate_data.py
Generates realistic sample e-commerce data (no Kaggle download needed).
Run this once before launching the dashboard.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os


def generate_ecommerce_data():
    np.random.seed(42)
    random.seed(42)

    n_customers = 1000
    n_orders = 5000

    states = ['CA', 'TX', 'NY', 'FL', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI',
              'WA', 'AZ', 'CO', 'MA', 'TN']

    cities_by_state = {
        'CA': ['Los Angeles', 'San Francisco', 'San Diego'],
        'TX': ['Houston', 'Dallas', 'Austin'],
        'NY': ['New York', 'Buffalo', 'Albany'],
        'FL': ['Miami', 'Orlando', 'Tampa'],
        'IL': ['Chicago', 'Springfield', 'Naperville'],
        'PA': ['Philadelphia', 'Pittsburgh', 'Allentown'],
        'OH': ['Columbus', 'Cleveland', 'Cincinnati'],
        'GA': ['Atlanta', 'Savannah', 'Augusta'],
        'NC': ['Charlotte', 'Raleigh', 'Durham'],
        'MI': ['Detroit', 'Grand Rapids', 'Lansing'],
        'WA': ['Seattle', 'Spokane', 'Tacoma'],
        'AZ': ['Phoenix', 'Tucson', 'Scottsdale'],
        'CO': ['Denver', 'Boulder', 'Colorado Springs'],
        'MA': ['Boston', 'Cambridge', 'Worcester'],
        'TN': ['Nashville', 'Memphis', 'Knoxville'],
    }

    # ── Products ──────────────────────────────────────────────
    product_catalog = {
        'Electronics':    [('Wireless Headphones', 80, 300), ('Smart Watch', 100, 500),
                           ('Bluetooth Speaker', 30, 150), ('USB-C Hub', 20, 80),
                           ('Webcam', 40, 180), ('Mechanical Keyboard', 50, 200),
                           ('Gaming Mouse', 25, 120), ('Portable Monitor', 120, 400),
                           ('Phone Case', 10, 40), ('Tablet Stand', 15, 60)],
        'Clothing':       [('T-Shirt', 10, 50), ('Jeans', 30, 100), ('Sneakers', 40, 150),
                           ('Winter Jacket', 60, 200), ('Summer Dress', 25, 90),
                           ('Hoodie', 30, 80), ('Running Shorts', 15, 55),
                           ('Ankle Socks', 5, 20), ('Cap', 10, 40), ('Scarf', 12, 45)],
        'Home & Kitchen': [('Coffee Maker', 40, 200), ('Air Fryer', 60, 180),
                           ('Blender', 30, 120), ('Toaster', 20, 80),
                           ('Knife Set', 30, 150), ('Cutting Board', 10, 50),
                           ('Mug Set', 15, 50), ('Storage Organizer', 20, 70),
                           ('LED Desk Lamp', 25, 90), ('Throw Pillow', 15, 60)],
        'Sports':         [('Yoga Mat', 20, 80), ('Adjustable Dumbbells', 50, 200),
                           ('Resistance Bands', 10, 40), ('Water Bottle', 15, 50),
                           ('Running Shoes', 50, 180), ('Jump Rope', 8, 30),
                           ('Foam Roller', 20, 60), ('Gym Bag', 25, 90),
                           ('Protein Shaker', 10, 35), ('Fitness Tracker', 30, 150)],
        'Books':          [('Python Programming', 20, 50), ('Data Science Handbook', 25, 60),
                           ('ML Engineering Guide', 22, 55), ('Business Strategy', 18, 45),
                           ('Self-Help Bestseller', 12, 30), ('Science Fiction Novel', 10, 25),
                           ('Cook Book', 15, 40), ('World History', 18, 45),
                           ('Travel Photography', 20, 50), ('Graphic Novel', 12, 30)],
        'Beauty':         [('Face Moisturizer', 15, 80), ('SPF Sunscreen', 12, 50),
                           ('Lipstick Set', 10, 45), ('Foundation', 15, 60),
                           ('Argan Shampoo', 10, 40), ('Hair Conditioner', 10, 40),
                           ('Perfume', 30, 150), ('Eye Cream', 20, 90),
                           ('Vitamin C Serum', 18, 80), ('Nail Polish Set', 8, 30)],
        'Toys':           [('LEGO Creator Set', 20, 100), ('Strategy Board Game', 15, 60),
                           ('1000-Piece Puzzle', 10, 40), ('Action Figure', 10, 40),
                           ('Collectible Doll', 15, 60), ('RC Racing Car', 20, 90),
                           ('Card Game Pack', 8, 25), ('Art & Craft Kit', 12, 45),
                           ('Science Experiment Kit', 15, 55), ('Plush Stuffed Animal', 10, 35)],
        'Food & Grocery': [('Whey Protein Bar', 15, 50), ('Premium Coffee Beans', 12, 45),
                           ('Matcha Green Tea', 10, 35), ('Granola Mix', 8, 25),
                           ('Extra Virgin Olive Oil', 10, 35), ('Artisan Pasta', 5, 20),
                           ('Mixed Nuts Pack', 10, 40), ('Raw Honey', 8, 30),
                           ('Multivitamins', 12, 45), ('Healthy Snack Box', 15, 50)],
    }

    products_list = []
    pid = 1
    for category, items in product_catalog.items():
        for name, low, high in items:
            products_list.append({
                'product_id':   f'PROD{pid:04d}',
                'product_name': name,
                'category':     category,
                'price':        round(random.uniform(low, high), 2),
            })
            pid += 1
    products = pd.DataFrame(products_list)

    # ── Customers ─────────────────────────────────────────────
    customer_states = np.random.choice(states, n_customers)
    customers = pd.DataFrame({
        'customer_id': [f'CUST{i:04d}' for i in range(1, n_customers + 1)],
        'city':        [random.choice(cities_by_state[s]) for s in customer_states],
        'state':       customer_states,
        'join_date':   [datetime(2022, 1, 1) + timedelta(days=random.randint(0, 730))
                        for _ in range(n_customers)],
    })

    # ── Orders (with seasonal spike in Nov-Dec) ───────────────
    month_weights = [0.06, 0.06, 0.07, 0.08, 0.08, 0.08,
                     0.07, 0.08, 0.08, 0.09, 0.12, 0.13]
    dates = []
    for _ in range(n_orders):
        year  = random.choice([2023, 2024])
        month = random.choices(range(1, 13), weights=month_weights)[0]
        day   = random.randint(1, 28)
        dates.append(datetime(year, month, day))

    orders = pd.DataFrame({
        'order_id':    [f'ORD{i:05d}' for i in range(1, n_orders + 1)],
        'customer_id': np.random.choice(customers['customer_id'], n_orders),
        'order_date':  dates,
        'status':      np.random.choice(
            ['Delivered', 'Shipped', 'Processing', 'Cancelled', 'Returned'],
            n_orders, p=[0.62, 0.15, 0.10, 0.09, 0.04]
        ),
    })

    # ── Order Items ───────────────────────────────────────────
    order_items_list = []
    for order_id in orders['order_id']:
        n_items = random.randint(1, 4)
        for _, product in products.sample(n_items).iterrows():
            qty = random.randint(1, 3)
            order_items_list.append({
                'order_id':     order_id,
                'product_id':   product['product_id'],
                'product_name': product['product_name'],
                'category':     product['category'],
                'quantity':     qty,
                'unit_price':   product['price'],
                'total_price':  round(product['price'] * qty, 2),
            })
    order_items = pd.DataFrame(order_items_list)

    # ── Save CSVs ─────────────────────────────────────────────
    os.makedirs('data', exist_ok=True)
    customers.to_csv('data/customers.csv',     index=False)
    products.to_csv('data/products.csv',       index=False)
    orders.to_csv('data/orders.csv',           index=False)
    order_items.to_csv('data/order_items.csv', index=False)

    print("✅ Sample data generated successfully!")
    print(f"   Customers  : {len(customers):,}")
    print(f"   Products   : {len(products):,}")
    print(f"   Orders     : {len(orders):,}")
    print(f"   Order Items: {len(order_items):,}")

    return customers, products, orders, order_items


if __name__ == '__main__':
    generate_ecommerce_data()
