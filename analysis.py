
from pathlib import Path
import pandas as pd

DATA_DIR = Path("data")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

csv_files = list(DATA_DIR.glob("*.csv"))

if not csv_files:
    raise FileNotFoundError(
        "No CSV file found in the data folder."
    )

df = pd.read_csv(csv_files[0])
df.columns = df.columns.str.strip()

# Normalize column names for reliable matching.
df.columns = [
    c.lower().strip().replace(" ", "_")
    for c in df.columns
]

print("Dataset loaded:", csv_files[0].name)
print("Original rows:", len(df))

# Convert numeric columns where available.
numeric_candidates = [
    "year", "month", "warehouse_sales",
    "retail_sales", "retail_transfers"
]

for col in numeric_candidates:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Remove duplicate records.
df = df.drop_duplicates()

# Keep rows with valid dates if year and month are available.
if {"year", "month"}.issubset(df.columns):
    df = df[
        df["year"].between(1900, 2100)
        & df["month"].between(1, 12)
    ].copy()

    df["period"] = pd.to_datetime(
        dict(
            year=df["year"].astype(int),
            month=df["month"].astype(int),
            day=1
        ),
        errors="coerce"
    )

# Report missing values before filling anything.
print("\nMissing values by column:")
print(df.isnull().sum().to_string())

# Save a cleaned copy; don't modify the original CSV.
clean_path = OUTPUT_DIR / "cleaned_retail_sales.csv"
df.to_csv(clean_path, index=False)

print("\nCleaned rows:", len(df))
print("Saved:", clean_path)

# Calculate summaries using the actual available columns.
if "warehouse_sales" in df.columns:
    print("\nTotal warehouse sales:")
    print(df["warehouse_sales"].sum())

if "retail_sales" in df.columns:
    print("\nTotal retail sales:")
    print(df["retail_sales"].sum())

if "description" in df.columns:
    sales_cols = [
        c for c in ["warehouse_sales", "retail_sales"]
        if c in df.columns
    ]

    if sales_cols:
        product_summary = (
            df.groupby("description", dropna=False)[sales_cols]
            .sum()
            .sort_values(sales_cols[0], ascending=False)
        )

        print("\nTop 10 products:")
        print(product_summary.head(10).to_string())

if "period" in df.columns:
    sales_cols = [
        c for c in ["warehouse_sales", "retail_sales"]
        if c in df.columns
    ]

    if sales_cols:
        monthly_summary = (
            df.groupby("period")[sales_cols]
            .sum()
            .sort_index()
        )

        monthly_summary.to_csv(
            OUTPUT_DIR / "monthly_sales_summary.csv"
        )

        print("\nMonthly sales summary:")
        print(monthly_summary.tail(12).to_string())

print("\nAnalysis completed successfully.")
