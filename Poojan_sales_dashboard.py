"""
Sales Data Analyst Dashboard
Frontend: Streamlit
Backend: pandas-based data loading, cleaning, filtering and KPI calculations
Data source: Excel workbook only (no database required).

Run:
    pip install -r requirements.txt
    streamlit run sales_dashboard.py
"""

from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
)

DEFAULT_FILE = Path("sales data .xlsx")

# ---------------- BACKEND ----------------
@st.cache_data
def load_data(file_path: str) -> pd.DataFrame:
    """Load and standardize the Excel sales dataset."""
    df = pd.read_excel(file_path)

    # Standardize text fields without changing the original numeric values.
    text_cols = df.select_dtypes(include="object").columns
    for col in text_cols:
        df[col] = df[col].astype("string").str.strip()

    if "Order_Date" in df.columns:
        df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")

    # Normalize common categorical inconsistencies.
    if "Product_Category" in df.columns:
        df["Product_Category"] = (
            df["Product_Category"].str.strip().str.title()
        )
    if "Order_Status" in df.columns:
        df["Order_Status"] = (
            df["Order_Status"].str.strip().str.title()
        )
    if "Payment_Method" in df.columns:
        df["Payment_Method"] = (
            df["Payment_Method"].str.strip().str.replace("_", " ", regex=False).str.title()
        )

    # Derived metrics.
    if "Sales_Amount" in df.columns and "Cost_Amount" in df.columns:
        df["Profit_Margin_%"] = (
            df["Profit"] / df["Sales_Amount"].replace(0, pd.NA) * 100
        )

    return df


def filter_data(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Apply dashboard filters and return a filtered dataframe."""
    result = df.copy()

    for col, selected in filters.items():
        if selected and selected != ["All"] and col in result.columns:
            result = result[result[col].isin(selected)]

    if filters.get("Date Range") and "Order_Date" in result.columns:
        start, end = filters["Date Range"]
        result = result[
            result["Order_Date"].between(pd.Timestamp(start), pd.Timestamp(end))
        ]

    return result


def calculate_kpis(df: pd.DataFrame) -> dict:
    """Calculate core business KPIs."""
    sales = df["Sales_Amount"].sum() if "Sales_Amount" in df else 0
    cost = df["Cost_Amount"].sum() if "Cost_Amount" in df else 0
    profit = df["Profit"].sum() if "Profit" in df else 0
    quantity = df["Quantity"].sum() if "Quantity" in df else 0
    orders = df["Order_ID"].nunique() if "Order_ID" in df else len(df)
    returns = (
        (df["Return_Flag"].astype("string").str.lower() == "yes").sum()
        if "Return_Flag" in df else 0
    )

    return {
        "Sales": sales,
        "Profit": profit,
        "Orders": orders,
        "Units": quantity,
        "Avg Order Value": sales / orders if orders else 0,
        "Profit Margin": (profit / sales * 100) if sales else 0,
        "Return Rate": (returns / len(df) * 100) if len(df) else 0,
        "Rows": len(df),
        "Cost": cost,
    }


def money(value):
    return f"${value:,.0f}"


# ---------------- FRONTEND ----------------
st.title("📊 Sales Data Analyst Dashboard")
st.caption("Excel-powered sales analytics • Python + Pandas + Plotly + Streamlit")

uploaded = st.sidebar.file_uploader(
    "Upload Excel file (optional)",
    type=["xlsx", "xls"],
    help="If you do not upload a file, the app reads 'sales data .xlsx' from the project folder.",
)

if uploaded is not None:
    df = load_data(uploaded)
else:
    if not DEFAULT_FILE.exists():
        st.error(
            "Excel file not found. Put 'sales data .xlsx' beside sales_dashboard.py "
            "or upload it from the sidebar."
        )
        st.stop()
    df = load_data(str(DEFAULT_FILE))

st.sidebar.header("🔎 Filters")

def options_for(col):
    if col not in df.columns:
        return ["All"]
    values = sorted(df[col].dropna().astype(str).unique().tolist())
    return ["All"] + values

selected_category = st.sidebar.multiselect(
    "Product Category",
    options_for("Product_Category"),
    default=["All"],
)
selected_channel = st.sidebar.multiselect(
    "Sales Channel",
    options_for("Sales_Channel"),
    default=["All"],
)
selected_country = st.sidebar.multiselect(
    "Country",
    options_for("Country"),
    default=["All"],
)
selected_segment = st.sidebar.multiselect(
    "Customer Segment",
    options_for("Customer_Segment"),
    default=["All"],
)

date_filter = None
if "Order_Date" in df.columns and df["Order_Date"].notna().any():
    min_date = df["Order_Date"].min().date()
    max_date = df["Order_Date"].max().date()
    date_filter = st.sidebar.date_input(
        "Order Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if isinstance(date_filter, tuple) and len(date_filter) == 2:
        date_filter = date_filter

filters = {
    "Product_Category": selected_category,
    "Sales_Channel": selected_channel,
    "Country": selected_country,
    "Customer_Segment": selected_segment,
    "Date Range": date_filter,
}

filtered = filter_data(df, filters)
kpi = calculate_kpis(filtered)

# KPI cards
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Total Sales", money(kpi["Sales"]))
c2.metric("Profit", money(kpi["Profit"]))
c3.metric("Orders", f'{kpi["Orders"]:,}')
c4.metric("Units Sold", f'{kpi["Units"]:,}')
c5.metric("Profit Margin", f'{kpi["Profit Margin"]:.1f}%')
c6.metric("Return Rate", f'{kpi["Return Rate"]:.1f}%')

st.divider()

# Row 1: trend + category
left, right = st.columns(2)

with left:
    st.subheader("📈 Sales & Profit Trend")
    if "Order_Date" in filtered.columns and len(filtered):
        trend = (
            filtered.dropna(subset=["Order_Date"])
            .assign(Month=lambda x: x["Order_Date"].dt.to_period("M").astype(str))
            .groupby("Month", as_index=False)[["Sales_Amount", "Profit"]]
            .sum()
        )
        if len(trend):
            trend_long = trend.melt(
                id_vars="Month",
                value_vars=["Sales_Amount", "Profit"],
                var_name="Metric",
                value_name="Amount",
            )
            fig = px.line(
                trend_long,
                x="Month",
                y="Amount",
                color="Metric",
                markers=True,
                labels={"Amount": "Amount", "Month": "Month"},
            )
            fig.update_layout(legend_title_text="")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough date data for a trend.")
    else:
        st.info("No records match the current filters.")

with right:
    st.subheader("🧩 Sales by Product Category")
    if len(filtered) and "Product_Category" in filtered.columns:
        cat = (
            filtered.groupby("Product_Category", as_index=False)["Sales_Amount"]
            .sum()
            .sort_values("Sales_Amount", ascending=False)
        )
        fig = px.bar(
            cat,
            x="Sales_Amount",
            y="Product_Category",
            orientation="h",
            text_auto=".2s",
            labels={"Sales_Amount": "Sales", "Product_Category": "Category"},
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No category data available.")

# Row 2
left, right = st.columns(2)

with left:
    st.subheader("🌍 Sales by Country")
    if len(filtered) and "Country" in filtered.columns:
        country = (
            filtered.groupby("Country", as_index=False)["Sales_Amount"]
            .sum()
            .sort_values("Sales_Amount", ascending=False)
        )
        fig = px.bar(
            country,
            x="Country",
            y="Sales_Amount",
            text_auto=".2s",
            labels={"Sales_Amount": "Sales"},
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No country data available.")

with right:
    st.subheader("🛒 Sales Channel Mix")
    if len(filtered) and "Sales_Channel" in filtered.columns:
        channel = (
            filtered.groupby("Sales_Channel", as_index=False)["Sales_Amount"]
            .sum()
            .sort_values("Sales_Amount", ascending=False)
        )
        fig = px.pie(
            channel,
            names="Sales_Channel",
            values="Sales_Amount",
            hole=0.45,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No channel data available.")

# Row 3: products + returns
left, right = st.columns(2)

with left:
    st.subheader("🏆 Top 10 Products by Sales")
    if len(filtered) and "Product_Name" in filtered.columns:
        products = (
            filtered.groupby("Product_Name", as_index=False)["Sales_Amount"]
            .sum()
            .sort_values("Sales_Amount", ascending=False)
            .head(10)
        )
        fig = px.bar(
            products.sort_values("Sales_Amount"),
            x="Sales_Amount",
            y="Product_Name",
            orientation="h",
            text_auto=".2s",
            labels={"Sales_Amount": "Sales", "Product_Name": "Product"},
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No product data available.")

with right:
    st.subheader("↩️ Return Analysis")
    if len(filtered) and "Return_Flag" in filtered.columns:
        ret = (
            filtered.assign(
                Return_Flag=filtered["Return_Flag"].astype("string").str.title()
            )
            .groupby("Return_Flag", as_index=False)
            .agg(
                Transactions=("Transaction_ID", "count"),
                Sales=("Sales_Amount", "sum"),
            )
        )
        fig = px.bar(
            ret,
            x="Return_Flag",
            y="Transactions",
            text="Transactions",
            labels={"Return_Flag": "Return Flag"},
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No return data available.")

# Data quality / table
st.divider()
st.subheader("🧹 Data Quality Snapshot")
q1, q2, q3 = st.columns(3)
q1.metric("Filtered Rows", f"{len(filtered):,}")
q2.metric("Missing Cells", f"{int(filtered.isna().sum().sum()):,}")
q3.metric("Columns", f"{filtered.shape[1]:,}")

with st.expander("Preview filtered data"):
    st.dataframe(filtered.head(500), use_container_width=True)

csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download Filtered CSV",
    data=csv,
    file_name="filtered_sales_data.csv",
    mime="text/csv",
)

st.caption(
    "Note: This dashboard is designed for analysis of the supplied structured Excel dataset. "
    "No database or external API is required."
)
