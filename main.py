import pandas as pd
import os
import logging
import time
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
from divider import divider

log_file = "logs.txt"

logging.basicConfig(
    filename=log_file,
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    force=True,
)

def prismaflow_pipeline(
    df,
    target_col=None,
    manual_columns=None,
    outlier_skipping=None,
    columns_to_keep=None,
    output_file="processed_dataset.csv",
    return_df=False,
):

    if df is None:

        logging.error("DataFrame is None")

        return None if return_df else False

    logging.info(f"Starting Prismaflow Pipeline")
    start_time = time.time()
    divider()

    row_number_col = "row_number"
    keep = list(columns_to_keep or [])

    df[row_number_col] = range(1, len(df) + 1)

    y = None

    df, y = remove_target(df, target_col, id_col=row_number_col)

    df = remove_columns(df, manual_columns, exclude_cols=keep)

    df = clear_columns(df, exclude_cols=keep)

    df = clear_null_values(df, 0.05, exclude_cols=keep)

    df = finalize_dtypes(df, exclude_cols=keep)

    if outlier_skipping is not None:

        df = remove_outliers(df, True, exclude_cols=[row_number_col, *keep, *outlier_skipping])

    else:
        df = remove_outliers(df, True, exclude_cols=[row_number_col, *keep])

    df = encode_features(df, "label", exclude_cols=keep)

    df = feature_selection(df, exclude_cols=[row_number_col, *keep])

    df = extract_temporal_features(df, exclude_cols=keep)

    df = scale_features(df, "standard", exclude_cols=[row_number_col, *keep])

    df = add_target(df, y, target_col, key_col=row_number_col)

    df.drop(columns=[row_number_col], inplace=True, errors="ignore")

    end_time = time.time()

    time_elapsed = end_time - start_time

    logging.info("Pipeline completed successfully")

    divider()

    logging.info(f"Time elapsed: {round(time_elapsed, 2)} seconds")
    
    divider()

    if output_file:
        export_file(df, output_file)

    return df if return_df else True
    