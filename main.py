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

df = pd.read_csv(csv_file)

df, y = remove_target(df, target_col)

df = clear_columns(df)

df = clear_null_values(df, 0.05)

df = finalize_dtypes(df)

df = remove_columns(df, None)

df = remove_outliers(df, True)

df = encode_features(df, "label")

df = feature_selection(df)

df = extract_temporal_features(df)

df = scale_features(df, "standard")

df = add_target(df, y, target_col)

export_file(df, "processed_dataset.csv")
