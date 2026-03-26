import pandas as pd
import streamlit as st

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="B2B Dashboard", layout="wide")

# ---------------- TITLE ----------------
st.title("📊 B2B Sales Intelligence Dashboard")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    df = pd.read_excel("B2B_Dataset_1000_Rows.xlsx")
    df['Last_Purchase_Date'] = pd.to_datetime(df['Last_Purchase_Date'])
    return df

df = load_data()

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("🔍 Filters")

region_filter = st.sidebar.multiselect(
    "Select Region",
    options=df['Region'].unique(),
    default=df['Region'].unique()
)

category_filter = st.sidebar.multiselect(
    "Select Product Category",
    options=df['Product_Category'].unique(),
    default=df['Product_Category'].unique()
)

# Apply filters
filtered_df = df[
    (df['Region'].isin(region_filter)) &
    (df['Product_Category'].isin(category_filter))
]

# ---------------- KPI SECTION ----------------
st.subheader("📌 Key Performance Indicators")

total_sales = filtered_df['Revenue'].sum()
total_customers = filtered_df['Client_ID'].nunique()
repeat_customers = filtered_df[filtered_df['Purchase_Frequency'] > 1]['Client_ID'].nunique()

if total_customers > 0:
    success_rate = (repeat_customers / total_customers) * 100
else:
    success_rate = 0

col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Total Sales", f"{total_sales:,.0f}")
col2.metric("👥 Total Customers", total_customers)
col3.metric("🔁 Repeat Customers", repeat_customers)
col4.metric("📈 Success Rate (%)", f"{success_rate:.2f}%")

# ---------------- CHARTS ----------------

st.subheader("📊 Product Category Performance")
cat_sales = filtered_df.groupby('Product_Category')['Revenue'].sum()
st.bar_chart(cat_sales)

st.subheader("📈 Customer Purchase Trends")
trend = filtered_df.groupby('Last_Purchase_Date')['Revenue'].sum()
trend = trend.sort_index()
st.line_chart(trend)

st.subheader("🌍 Region-wise Sales")
region_sales = filtered_df.groupby('Region')['Revenue'].sum()
st.bar_chart(region_sales)

# ---------------- EXTRA INSIGHTS ----------------

st.subheader("📊 Top 5 Customers by Revenue")
top_customers = (
    filtered_df.groupby('Client_ID')['Revenue']
    .sum()
    .sort_values(ascending=False)
    .head(5)
)
st.dataframe(top_customers)

st.subheader("📦 Top 5 Products by Revenue")
top_products = (
    filtered_df.groupby('Product_ID')['Revenue']
    .sum()
    .sort_values(ascending=False)
    .head(5)
)
st.dataframe(top_products)

# ---------------- FOOTER ----------------
st.markdown("---")
st.write("✅ Dashboard built using Streamlit for B2B Sales Analysis")
