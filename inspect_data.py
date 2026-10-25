
from pathlib import Path
import pandas as pd

data_folder = Path("data")
csv_files = list(data_folder.glob("*.csv"))

if not csv_files:
    print("No CSV file found in the data folder.")
    print("Please download and extract the dataset first.")
else:
    file_path = csv_files[0]
    print(f"\nDataset found: {file_path.name}")

    df = pd.read_csv(file_path)

    print("\n--- Dataset dimensions ---")
    print(f"Rows: {df.shape[0]:,}")
    print(f"Columns: {df.shape[1]}")

    print("\n--- Column names ---")
    print(df.columns.tolist())

    print("\n--- First 5 rows ---")
    print(df.head().to_string())

    print("\n--- Missing values ---")
    print(df.isnull().sum().to_string())
