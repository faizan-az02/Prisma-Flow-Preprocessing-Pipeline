import pandas as pd
import os
import logging
from null_values import clear_null_values
from clear_columns import clear_columns
from finalize_types import finalize_dtypes
from outliers_removal import remove_outliers

log_file = "log.txt"

logging.basicConfig(
    filename=log_file,
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    force=True,
)

df = pd.read_csv('accounts.csv')

df = clear_columns(df)

df = clear_null_values(df, 0.05)

df = finalize_dtypes(df)

df = remove_outliers(df)

print(df.head())

print(df.info())

print(df.describe())