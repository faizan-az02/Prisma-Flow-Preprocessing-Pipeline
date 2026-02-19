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

scaling_skipping = _parse_csv_list(input("Enter the scaling skipping columns, separated by commas (blank for none): "))

outlier_method = input("Enter outlier method (iqr, zscore, modified_zscore) [iqr]: ").strip() or "iqr"
outlier_action = input("Enter outlier action (skip, remove, cap) [remove]: ").strip() or "remove"
raw_outlier_param = input("Enter outlier method value (blank for default): ").strip()
outlier_param = None
if raw_outlier_param != "":
    try:
        outlier_param = float(raw_outlier_param)
    except Exception:
        outlier_param = None

ok = prismaflow_pipeline(
    df,
    target_col=target_col,
    manual_columns=manual_columns,
    outlier_skipping=outlier_skipping,
    columns_to_keep=columns_to_keep,
    scaling_skipping=scaling_skipping,
    outlier_method=outlier_method,
    handle_outliers=(outlier_action != "skip"),
    outlier_drop=(outlier_action != "cap"),
    outlier_param=outlier_param,
    output_file="processed_dataset.csv",
    return_df=False,
)

if ok is False:
    print("Pipeline failed")
    exit(1)

print("Pipeline completed successfully")

