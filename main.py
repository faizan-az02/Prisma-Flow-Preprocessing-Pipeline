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

log_file = "logs.txt"

logging.basicConfig(
    filename=log_file,
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    force=True,
)

def prismaflow_pipeline(input_file):

    df = pd.read_csv(input_file)

    df = clear_columns(df)

    df = clear_null_values(df, 0.05)

    df = finalize_dtypes(df)

    df = remove_columns(df, ["Note", "username"])

    df = remove_outliers(df, True)

    df = encode_features(df, "label")

    df = feature_selection(df)

    df = extract_temporal_features(df)

    df = scale_features(df, "standard")

    export_file(df, "processed_dataset.csv")

if __name__ == "__main__":

    input_file = "accounts.csv"

    prismaflow_pipeline(input_file)