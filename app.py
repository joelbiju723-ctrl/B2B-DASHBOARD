import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE ----------------
st.set_page_config(page_title="B2B Dashboard", layout="wide")

# ---------------- LOAD DATA ----------------
uploaded = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded is None:
    st.title("📊 B2B Sales Intelligence Dashboard")
    st.info("Upload your dataset to continue")
    st.stop()

df = pd.read_excel(uploaded)
df['Last_Purchase_Date'] = pd.to_datetime(df['Last_Purchase_Date'])

# ---------------- HEADER ----------------
st.title("📊 B2B Sales Intelligence Dashboard")
st.caption("Part C: KPIs & Charts | Part D: Insights")

# ---------------- KPIs ----------------
st.subheader("📌 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

total_sales = len(df)
repeat_customers = df[df['Purchase_Frequency'] > 1]['Client_ID'].nunique()
success_rate = (repeat_customers / df['Client_ID'].nunique()) * 100
total_revenue = df['Revenue'].sum()

col1.metric("Total Sales", total_sales)
col2.metric("Repeat Customers", repeat_customers)
col3.metric("Success Rate", f"{success_rate:.1f}%")
col4.metric("Revenue", f"${total_revenue:,.0f}")

# ---------------- CHARTS ----------------
st.subheader("📊 Charts")

# Category
cat = df.groupby('Product_Category')['Revenue'].sum().reset_index()
fig1 = px.bar(cat, x='Product_Category', y='Revenue', title="Category Performance")
st.plotly_chart(fig1, use_container_width=True)

# Trend
trend = df.groupby('Last_Purchase_Date')['Revenue'].sum().reset_index()
fig2 = px.line(trend, x='Last_Purchase_Date', y='Revenue', title="Purchase Trend")
st.plotly_chart(fig2, use_container_width=True)

# Region
reg = df.groupby('Region')['Revenue'].sum().reset_index()
fig3 = px.bar(reg, x='Region', y='Revenue', title="Region Sales")
st.plotly_chart(fig3, use_container_width=True)

# ---------------- INSIGHTS ----------------
st.subheader("📌 Insights")

st.write("✔ High frequency customers generate more revenue")
st.write("✔ Some regions show stronger repeat purchases")
st.write("✔ Product bundling can increase sales")
