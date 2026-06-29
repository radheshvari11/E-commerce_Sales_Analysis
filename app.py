"""
app.py  –  E-Commerce Sales Analytics Dashboard
Run: streamlit run app.py
"""

import os
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from generate_data import generate_ecommerce_data

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="E-Commerce Sales Dashboard",
    page_icon="🛒",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="metric-container"] {
    background-color: #f0f2f6;
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 12px 16px;
}
</style>
""", unsafe_allow_html=True)


# ── Data loading ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    if not os.path.exists("data/orders.csv"):
        generate_ecommerce_data()

    customers   = pd.read_csv("data/customers.csv",   parse_dates=["join_date"])
    orders      = pd.read_csv("data/orders.csv",      parse_dates=["order_date"])
    order_items = pd.read_csv("data/order_items.csv")

    # Master flat table
    df = (order_items
          .merge(orders[["order_id", "customer_id", "order_date", "status"]], on="order_id")
          .merge(customers[["customer_id", "state", "city"]], on="customer_id"))
    return df, customers, orders


df, customers, orders = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🔍 Filters")
    st.markdown("---")

    min_date = df["order_date"].min().date()
    max_date = df["order_date"].max().date()
    date_range = st.date_input("📅 Date Range", [min_date, max_date],
                               min_value=min_date, max_value=max_date)

    categories = ["All"] + sorted(df["category"].unique().tolist())
    sel_cat = st.selectbox("🏷️ Category", categories)

    statuses = ["All"] + sorted(df["status"].unique().tolist())
    sel_status = st.selectbox("📦 Order Status", statuses)

    states = ["All"] + sorted(df["state"].unique().tolist())
    sel_state = st.selectbox("📍 State", states)

    st.markdown("---")
    st.info("📊 Data: Jan 2023 – Dec 2024\n\n"
            "🛒 5,000 orders · 1,000 customers · 80 products")

# ── Apply filters ─────────────────────────────────────────────────────────────
fdf = df.copy()
if len(date_range) == 2:
    fdf = fdf[(fdf["order_date"].dt.date >= date_range[0]) &
              (fdf["order_date"].dt.date <= date_range[1])]
if sel_cat    != "All": fdf = fdf[fdf["category"] == sel_cat]
if sel_status != "All": fdf = fdf[fdf["status"]   == sel_status]
if sel_state  != "All": fdf = fdf[fdf["state"]    == sel_state]

delivered = fdf[fdf["status"] == "Delivered"]

# ── KPI row ───────────────────────────────────────────────────────────────────
st.title("🛒 E-Commerce Sales Analytics Dashboard")
st.caption("Interactive insights into sales, customers, and product performance.")
st.markdown("---")

total_revenue  = delivered["total_price"].sum()
total_orders   = fdf["order_id"].nunique()
aov            = delivered.groupby("order_id")["total_price"].sum().mean()
total_cust     = fdf["customer_id"].nunique()

c1, c2, c3, c4 = st.columns(4)
c1.metric("💰 Total Revenue",    f"${total_revenue:,.0f}")
c2.metric("📦 Total Orders",     f"{total_orders:,}")
c3.metric("🛍️ Avg Order Value",  f"${aov:,.2f}" if not np.isnan(aov) else "$0.00")
c4.metric("👥 Unique Customers", f"{total_cust:,}")

st.markdown("---")

# ── Revenue over time + Category donut ───────────────────────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📈 Revenue Over Time")
    rev_time = delivered.copy()
    rev_time["month"] = rev_time["order_date"].dt.to_period("M").astype(str)
    monthly = rev_time.groupby("month")["total_price"].sum().reset_index()
    monthly.columns = ["Month", "Revenue"]
    fig = px.line(monthly, x="Month", y="Revenue", markers=True,
                  color_discrete_sequence=["#636EFA"])
    fig.update_layout(xaxis_tickangle=-45, height=350, margin=dict(t=20))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🏷️ Sales by Category")
    cat_rev = (delivered.groupby("category")["total_price"]
               .sum().reset_index()
               .rename(columns={"category": "Category", "total_price": "Revenue"}))
    fig = px.pie(cat_rev, values="Revenue", names="Category", hole=0.4)
    fig.update_layout(height=350, margin=dict(t=20))
    st.plotly_chart(fig, use_container_width=True)

# ── Top products + Order status ───────────────────────────────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🏆 Top 10 Products by Revenue")
    top10 = (delivered.groupby("product_name")["total_price"]
             .sum().nlargest(10).reset_index()
             .rename(columns={"product_name": "Product", "total_price": "Revenue"})
             .sort_values("Revenue"))
    fig = px.bar(top10, x="Revenue", y="Product", orientation="h",
                 color="Revenue", color_continuous_scale="Blues")
    fig.update_layout(height=380, showlegend=False, margin=dict(t=20))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📦 Order Status Breakdown")
    status_cnt = (fdf.groupby("status")["order_id"]
                  .nunique().reset_index()
                  .rename(columns={"status": "Status", "order_id": "Count"}))
    color_map = {
        "Delivered":  "#00CC96", "Shipped": "#636EFA",
        "Processing": "#FFA15A", "Cancelled": "#EF553B", "Returned": "#AB63FA"
    }
    fig = px.pie(status_cnt, values="Count", names="Status",
                 color="Status", color_discrete_map=color_map)
    fig.update_layout(height=380, margin=dict(t=20))
    st.plotly_chart(fig, use_container_width=True)

# ── Revenue by state ──────────────────────────────────────────────────────────
st.subheader("🗺️ Revenue by State")
state_rev = (delivered.groupby("state")["total_price"]
             .sum().reset_index()
             .rename(columns={"state": "State", "total_price": "Revenue"})
             .sort_values("Revenue", ascending=False))
fig = px.bar(state_rev, x="State", y="Revenue",
             color="Revenue", color_continuous_scale="Viridis")
fig.update_layout(height=350, margin=dict(t=20))
st.plotly_chart(fig, use_container_width=True)

# ── Monthly sales heatmap ─────────────────────────────────────────────────────
st.subheader("📅 Sales Heatmap (Month × Year)")
heat_df = delivered.copy()
heat_df["year"]  = heat_df["order_date"].dt.year.astype(str)
heat_df["month_num"] = heat_df["order_date"].dt.month
heat_df["month_name"] = heat_df["order_date"].dt.strftime("%b")
pivot = heat_df.pivot_table(values="total_price", index="month_name",
                             columns="year", aggfunc="sum")
month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
pivot = pivot.reindex([m for m in month_order if m in pivot.index])
fig = px.imshow(pivot, color_continuous_scale="Blues", aspect="auto",
                labels=dict(color="Revenue ($)"))
fig.update_layout(height=350, margin=dict(t=20))
st.plotly_chart(fig, use_container_width=True)

# ── Raw data expander ─────────────────────────────────────────────────────────
with st.expander("📋 View Raw Data (first 200 rows)"):
    st.dataframe(fdf.head(200), use_container_width=True)

st.markdown("---")
st.caption("Built with Python · Pandas · Plotly · Streamlit  |  E-Commerce Sales Analysis Portfolio Project")

