import pandas as pd

from main import prismaflow_pipeline


def _parse_csv_list(raw: str) -> list[str] | None:
    raw = (raw or "").strip()
    if raw == "":
        return None
    items = [c.strip() for c in raw.split(",") if c.strip()]
    return items or None

csv_file = input("Enter the csv file name (without .csv): ").strip()

csv_path = f"{csv_file}.csv"

df = pd.read_csv(csv_path)

print(df.head())

target_col = input("Enter the target column (blank for none): ").strip()

if target_col == "" or target_col not in df.columns:

    target_col = None

manual_columns = _parse_csv_list(input("Enter the manual columns to remove, separated by commas (blank for none): "))

outlier_skipping = _parse_csv_list(input("Enter the outlier skipping columns, separated by commas (blank for none): "))

columns_to_keep = _parse_csv_list(input("Enter the columns to keep, separated by commas (blank for none): "))

ok = prismaflow_pipeline(
    df,
    target_col=target_col,
    manual_columns=manual_columns,
    outlier_skipping=outlier_skipping,
    columns_to_keep=columns_to_keep,
    output_file="processed_dataset.csv",
    return_df=False,
)

if ok is False:
    print("Pipeline failed")
    exit(1)
    
print("Pipeline completed successfully")

