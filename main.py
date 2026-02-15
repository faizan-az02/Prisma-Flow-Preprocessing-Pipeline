import pandas as pd
import os
import logging
from null_values import clear_null_values
from clear_columns import clear_columns
from finalize_types import finalize_dtypes
from outliers_removal import remove_outliers
from remove_columns import remove_columns
from encoding import encode_features
from scaling import scale_features
from feature_selection import feature_selection
from export_file import export_file
from temporal_features import extract_temporal_features
from remove_target import remove_target
from add_target import add_target

log_file = "logs.txt"

logging.basicConfig(
    filename=log_file,
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    force=True,
)

csv_file = "housing.csv"

target_col = "median_house_value"
row_number_col = "row_number"

df = pd.read_csv(csv_file)

# Manual row numbers: 1..N (stable ID for re-attaching target after row drops)
df[row_number_col] = range(1, len(df) + 1)

df, y = remove_target(df, target_col, id_col=row_number_col)

df = clear_columns(df)

df = clear_null_values(df, 0.05)

df = finalize_dtypes(df)

df = remove_columns(df, None)

df = remove_outliers(df, True, exclude_cols=[row_number_col])

df = encode_features(df, "label")

df = feature_selection(df, exclude_cols=[row_number_col])

df = extract_temporal_features(df)

df = scale_features(df, "standard", exclude_cols=[row_number_col])

df = add_target(df, y, target_col, key_col=row_number_col)

export_file(df, "processed_dataset.csv")
