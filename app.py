
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="RetailPulse",
    page_icon="📊",
    layout="wide"
)

st.title("📊 RetailPulse")
st.subheader("Big Data Sales Analytics Dashboard")
st.caption(
    "Explore retail and warehouse sales, product performance "
    "and monthly trends."
)

# Locate the dataset.
data_dir = Path("data")
csv_files = list(data_dir.glob("*.csv"))

if not csv_files:
    st.error("No CSV file found inside the data folder.")
    st.stop()

@st.cache_data
def load_data(file_path, modified_time):
    data = pd.read_csv(file_path)
    data.columns = [
        c.strip().lower().replace(" ", "_")
        for c in data.columns
    ]
    return data

file_path = csv_files[0]
df = load_data(str(file_path), file_path.stat().st_mtime)

# Recognize common column-name variations.
def find_column(candidates):
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
    return None

year_col = find_column(["year"])
month_col = find_column(["month"])
type_col = find_column(["type", "item_type"])
description_col = find_column(["description", "item_description"])
retail_col = find_column(["retail_sales", "retail_sales_units"])
warehouse_col = find_column(["warehouse_sales", "warehouse_sales_units"])
transfer_col = find_column(["retail_transfers", "retail_transfer"])

# Convert available measures to numeric.
measure_cols = [
    c for c in [retail_col, warehouse_col, transfer_col]
    if c is not None
]

for col in measure_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Sidebar filters.
st.sidebar.header("Dashboard Filters")
filtered = df.copy()

if year_col:
    years = sorted(df[year_col].dropna().unique().tolist())
    selected_years = st.sidebar.multiselect(
        "Select year",
        years,
        default=years
    )
    filtered = filtered[filtered[year_col].isin(selected_years)]

if type_col:
    types = sorted(
        filtered[type_col].dropna().astype(str).unique().tolist()
    )
    selected_types = st.sidebar.multiselect(
        "Select product type",
        types,
        default=types
    )
    filtered = filtered[
        filtered[type_col].astype(str).isin(selected_types)
    ]

# KPI cards.
kpis = st.columns(4)

kpis[0].metric("Records Analyzed", f"{len(filtered):,}")

if retail_col:
    kpis[1].metric(
        "Total Retail Sales",
        f"{filtered[retail_col].sum(skipna=True):,.0f}"
    )
else:
    kpis[1].metric("Retail Sales", "Column unavailable")

if warehouse_col:
    kpis[2].metric(
        "Total Warehouse Sales",
        f"{filtered[warehouse_col].sum(skipna=True):,.0f}"
    )
else:
    kpis[2].metric("Warehouse Sales", "Column unavailable")

if transfer_col:
    kpis[3].metric(
        "Total Retail Transfers",
        f"{filtered[transfer_col].sum(skipna=True):,.0f}"
    )
else:
    kpis[3].metric("Retail Transfers", "Column unavailable")

st.divider()

# Build a monthly trend chart.
st.subheader("📈 Monthly Sales Trends")

if year_col and month_col and measure_cols:
    chart_df = filtered.copy()
    chart_df[year_col] = pd.to_numeric(
        chart_df[year_col], errors="coerce"
    )
    chart_df[month_col] = pd.to_numeric(
        chart_df[month_col], errors="coerce"
    )

    chart_df = chart_df.dropna(subset=[year_col, month_col])
    chart_df = chart_df[
        chart_df[month_col].between(1, 12)
    ].copy()

    chart_df["Period"] = pd.to_datetime(
        dict(
            year=chart_df[year_col].astype(int),
            month=chart_df[month_col].astype(int),
            day=1
        ),
        errors="coerce"
    )

    monthly = (
        chart_df.groupby("Period")[measure_cols]
        .sum()
        .reset_index()
        .sort_values("Period")
    )

    if not monthly.empty:
        long_monthly = monthly.melt(
            id_vars="Period",
            value_vars=measure_cols,
            var_name="Measure",
            value_name="Sales"
        )

        fig = px.line(
            long_monthly,
            x="Period",
            y="Sales",
            color="Measure",
            markers=True,
            title="Monthly retail and warehouse activity"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No valid year/month combinations found.")
else:
    st.info(
        "Monthly trends require year, month, and at least one "
        "recognized sales column."
    )

# Product performance chart.
st.subheader("🏆 Product Performance")

if description_col and measure_cols:
    product_col = st.selectbox(
        "Choose measure for product ranking",
        measure_cols
    )

    top_products = (
        filtered.groupby(description_col)[product_col]
        .sum()
        .nlargest(10)
        .sort_values()
        .reset_index()
    )

    fig = px.bar(
        top_products,
        x=product_col,
        y=description_col,
        orientation="h",
        title="Top 10 products by selected measure",
        labels={
            product_col: product_col.replace("_", " ").title(),
            description_col: "Product"
        }
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info(
        "Product ranking requires a description column "
        "and a recognized numeric measure."
    )


# Seasonal Demand Analysis
st.divider()
st.header("Seasonal Demand Analysis")

if year_col and month_col and measure_cols:
    season_df = filtered.copy()

    season_df[year_col] = pd.to_numeric(
        season_df[year_col], errors="coerce"
    )
    season_df[month_col] = pd.to_numeric(
        season_df[month_col], errors="coerce"
    )

    season_df = season_df.dropna(
        subset=[year_col, month_col]
    )

    season_df = season_df[
        season_df[month_col].between(1, 12)
    ].copy()

    season_df["Month Name"] = season_df[month_col].astype(
        int
    ).map({
        1: "January", 2: "February", 3: "March",
        4: "April", 5: "May", 6: "June",
        7: "July", 8: "August", 9: "September",
        10: "October", 11: "November", 12: "December"
    })

    season_df["Season"] = season_df[month_col].astype(
        int
    ).map({
        12: "Winter", 1: "Winter", 2: "Winter",
        3: "Spring", 4: "Spring", 5: "Spring",
        6: "Summer", 7: "Summer", 8: "Summer",
        9: "Autumn", 10: "Autumn", 11: "Autumn"
    })

    selected_measure = st.selectbox(
        "Measure for seasonal analysis",
        measure_cols,
        key="season_measure"
    )

    monthly_pattern = (
        season_df.groupby("Month Name")[selected_measure]
        .mean()
        .reindex([
            "January", "February", "March", "April",
            "May", "June", "July", "August",
            "September", "October", "November", "December"
        ])
        .dropna()
        .reset_index(name="Average Activity")
    )

    if not monthly_pattern.empty:
        fig = px.bar(
            monthly_pattern,
            x="Month Name",
            y="Average Activity",
            title="Average Activity by Month",
            labels={"Month Name": "Month"}
        )
        st.plotly_chart(fig, use_container_width=True)

    seasonal_summary = (
        season_df.groupby("Season")[selected_measure]
        .agg(["mean", "sum", "count"])
        .reset_index()
        .rename(columns={
            "mean": "Average",
            "sum": "Total",
            "count": "Records"
        })
    )

    st.subheader("Seasonal Summary")
    st.dataframe(seasonal_summary, use_container_width=True)

    st.caption(
        "Seasons use a simple Northern Hemisphere calendar grouping. "
        "These are exploratory groupings, not proof that weather "
        "caused changes in demand."
    )
else:
    st.info(
        "Seasonal analysis requires year, month, and a numeric "
        "sales or activity column."
    )


# Demand Forecasting

# Demand Forecasting

# Demand Forecasting
st.header("Demand Forecasting")

forecast_options = [
    col for col in [retail_col, warehouse_col, transfer_col]
    if col is not None
    and col in df.columns
    and pd.api.types.is_numeric_dtype(df[col])
]

if year_col and month_col and forecast_options:
    forecast_measure = st.selectbox(
        "Choose a measure to forecast",
        forecast_options,
        key="forecast_measure"
    )

    forecast_data = df.copy()
    forecast_data[year_col] = pd.to_numeric(
        forecast_data[year_col], errors="coerce"
    )
    forecast_data[month_col] = pd.to_numeric(
        forecast_data[month_col], errors="coerce"
    )
    forecast_data[forecast_measure] = pd.to_numeric(
        forecast_data[forecast_measure], errors="coerce"
    )

    forecast_data = forecast_data.dropna(
        subset=[year_col, month_col, forecast_measure]
    )
    forecast_data = forecast_data[
        forecast_data[month_col].between(1, 12)
    ].copy()

    forecast_data["date"] = pd.to_datetime(
        {
            "year": forecast_data[year_col].astype(int),
            "month": forecast_data[month_col].astype(int),
            "day": 1
        },
        errors="coerce"
    )

    monthly_data = (
        forecast_data.dropna(subset=["date"])
        .groupby("date")[forecast_measure]
        .sum()
        .sort_index()
    )

    st.write("Valid historical months:", len(monthly_data))

    if len(monthly_data) >= 3:
        # Moving-average baseline forecast
        window = 3
        last_average = monthly_data.tail(window).mean()

        future_dates = pd.date_range(
            start=monthly_data.index[-1] + pd.offsets.MonthBegin(1),
            periods=3,
            freq="MS"
        )

        forecast_df = pd.DataFrame({
            "Month": future_dates,
            "Forecast": [max(0, last_average)] * len(future_dates)
        })

        st.subheader("Historical Monthly Activity")
        st.line_chart(
            monthly_data.rename("Historical activity")
        )

        st.subheader("Next 3 Months — Moving Average Forecast")
        st.line_chart(
            forecast_df.set_index("Month")["Forecast"]
        )

        display_forecast = forecast_df.copy()
        display_forecast["Month"] = (
            display_forecast["Month"].dt.strftime("%B %Y")
        )
        display_forecast["Forecast"] = (
            display_forecast["Forecast"].round(2)
        )

        st.dataframe(
            display_forecast,
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            "Baseline estimate based on the average of the last three "
            "observed months. Only nine months of historical data are "
            "available, so seasonality and forecast accuracy cannot be "
            "reliably established."
        )
    else:
        st.warning(
            "At least three valid historical months are needed "
            "for the moving-average forecast."
        )
else:
    st.info(
        "Forecasting requires year, month, and at least one recognized "
        "numeric sales or activity measure."
    )


# Data explorer.
with st.expander("🔎 Explore dataset"):
    st.write("Dataset shape:", filtered.shape)
    st.dataframe(filtered.head(100), use_container_width=True)

    st.download_button(
        "Download filtered data",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="retailpulse_filtered_data.csv",
        mime="text/csv"
    )

st.caption(
    "RetailPulse | Big Data Analytics Project | "
    "Forecasting will be added after validating the time series."
)
