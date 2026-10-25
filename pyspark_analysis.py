
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# Create a local Spark session
spark = (
    SparkSession.builder
    .appName("RetailPulseBigDataAnalysis")
    .master("local[*]")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

try:
    # Find the CSV dataset
    data_dir = Path("data")
    csv_files = list(data_dir.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            "No CSV file found inside the data folder."
        )

    csv_path = str(csv_files[0])

    # Read data with Spark
    df = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .option("mode", "DROPMALFORMED")
        .csv(csv_path)
    )

    # Normalize column names
    for old_name in df.columns:
        new_name = old_name.strip().lower().replace(" ", "_")
        if old_name != new_name:
            df = df.withColumnRenamed(old_name, new_name)

    print("\n===== RETAILPULSE PYSPARK ANALYSIS =====")
    print("Dataset row count:", df.count())
    print("Dataset columns:", df.columns)

    print("\n===== DATA SCHEMA =====")
    df.printSchema()

    # Find available columns
    year_col = "year" if "year" in df.columns else None
    month_col = "month" if "month" in df.columns else None

    measure_candidates = [
        "retail_sales",
        "retail_sales_units",
        "warehouse_sales",
        "warehouse_sales_units",
        "retail_transfers",
        "retail_transfer",
    ]

    measure_cols = [
        col for col in measure_candidates
        if col in df.columns
    ]

    if year_col and month_col and measure_cols:

        # Convert year and month to numeric values
        df = (
            df.withColumn(
                "year", F.col("year").cast("int")
            )
            .withColumn(
                "month", F.col("month").cast("int")
            )
        )

        # Convert measures safely; invalid text becomes NULL
        for col in measure_cols:
            df = df.withColumn(
                col,
                F.expr(f"try_cast(`{col}` AS DOUBLE)")
            )

        # Aggregate activity by year and month
        monthly_summary = (
            df.filter(
                F.col("year").isNotNull()
                & F.col("month").between(1, 12)
            )
            .groupBy("year", "month")
            .agg(
                *[
                    F.sum(F.col(col)).alias(f"total_{col}")
                    for col in measure_cols
                ],
                F.count("*").alias("record_count")
            )
            .orderBy("year", "month")
        )

        print("\n===== MONTHLY SALES SUMMARY =====")
        monthly_summary.show(50, truncate=False)

        # Save output using Pandas to avoid Spark's
        # Windows Hadoop output-permission issue
        output_dir = Path("outputs")
        output_dir.mkdir(parents=True, exist_ok=True)

        monthly_summary.toPandas().to_csv(
            output_dir / "pyspark_monthly_summary.csv",
            index=False
        )

        print("\nMonthly summary saved successfully.")
        print(
            "File location: outputs/pyspark_monthly_summary.csv"
        )

    else:
        print(
            "\nCould not create monthly summary. "
            "Check the year, month, and measure column names."
        )

finally:
    spark.stop()
