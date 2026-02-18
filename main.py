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
    scaling_skipping=None,
    handle_outliers=True,
    null_threshold=0.05,
    encoding_method="label",
    steps=None,
    scaling_method="standard",
    output_file="processed_dataset.csv",
    return_df=False,
    collect_metrics=False,
):

    if df is None:

        logging.error("DataFrame is None")

        if collect_metrics and return_df:
            return None, {"error": "DataFrame is None"}
        return None if return_df else False

    logging.info(f"Starting Prismaflow Pipeline")
    start_time = time.time()
    divider()

    row_number_col = "row_number"
    keep = list(columns_to_keep or [])

    try:
        null_threshold = 0.05 if null_threshold is None else float(null_threshold)
    except Exception:
        null_threshold = 0.05
    null_threshold = max(0.0, min(1.0, null_threshold))

    encoding_method = (encoding_method or "label").strip().lower()
    if encoding_method not in {"label", "onehot"}:
        encoding_method = "label"

    handle_outliers = bool(handle_outliers)

    scaling_method = (scaling_method or "standard").strip().lower()
    if scaling_method not in {"standard", "minmax"}:
        scaling_method = "standard"

    outlier_skipping = list(outlier_skipping or [])
    scaling_skipping = list(scaling_skipping or [])

    all_steps = {
        "manual_columns",
        "drop_empty_columns",
        "handle_nulls",
        "finalize_dtypes",
        "handle_outliers",
        "encoding",
        "feature_selection",
        "temporal_features",
        "scaling",
    }
    enabled_steps = set(all_steps)
    if steps is not None:
        if isinstance(steps, (list, tuple, set)):
            enabled_steps = {str(s).strip() for s in steps if str(s).strip()} & all_steps
        else:
            enabled_steps = set(all_steps)

    metrics = None
    if collect_metrics:
        metrics = {
            "time_processed_seconds": None,
            "rows_dropped": 0,
            "rows_dropped_nulls": 0,
            "rows_dropped_outliers": 0,
            "outliers_removed": 0,
            "columns_removed": 0,
            "columns_removed_manual": 0,
            "columns_removed_empty": 0,
            "columns_removed_feature_selection": 0,
            "columns_removed_temporal": 0,
        }

    df[row_number_col] = range(1, len(df) + 1)

    y = None

    df, y = remove_target(df, target_col, id_col=row_number_col)

    if "manual_columns" in enabled_steps:
        cols_before = set(df.columns)
        df = remove_columns(df, manual_columns, exclude_cols=keep)
        if metrics is not None:
            dropped = (cols_before - set(df.columns)) - {row_number_col}
            metrics["columns_removed_manual"] += len(dropped)

    if "drop_empty_columns" in enabled_steps:
        cols_before = set(df.columns)
        df = clear_columns(df, exclude_cols=keep)
        if metrics is not None:
            dropped = (cols_before - set(df.columns)) - {row_number_col}
            metrics["columns_removed_empty"] += len(dropped)

    if "handle_nulls" in enabled_steps:
        rows_before = int(df.shape[0])
        df = clear_null_values(df, null_threshold, exclude_cols=keep)
        if metrics is not None:
            metrics["rows_dropped_nulls"] += max(0, rows_before - int(df.shape[0]))

    if "finalize_dtypes" in enabled_steps:
        df = finalize_dtypes(df, exclude_cols=keep)

    if handle_outliers and ("handle_outliers" in enabled_steps):
        rows_before = int(df.shape[0])
        df = remove_outliers(df, True, exclude_cols=[row_number_col, *outlier_skipping])
        if metrics is not None:
            dropped_rows = max(0, rows_before - int(df.shape[0]))
            metrics["rows_dropped_outliers"] += dropped_rows
            metrics["outliers_removed"] += dropped_rows

    if "encoding" in enabled_steps:
        df = encode_features(df, encoding_method, exclude_cols=keep)

    if "feature_selection" in enabled_steps:
        cols_before = set(df.columns)
        df = feature_selection(df, exclude_cols=[row_number_col, *keep])
        if metrics is not None:
            dropped = (cols_before - set(df.columns)) - {row_number_col}
            metrics["columns_removed_feature_selection"] += len(dropped)

    if "temporal_features" in enabled_steps:
        cols_before = set(df.columns)
        df = extract_temporal_features(df, exclude_cols=keep)
        if metrics is not None:
            dropped = (cols_before - set(df.columns)) - {row_number_col}
            metrics["columns_removed_temporal"] += len(dropped)

    if "scaling" in enabled_steps:
        df = scale_features(df, scaling_method, exclude_cols=[row_number_col, *scaling_skipping])

    df = add_target(df, y, target_col, key_col=row_number_col)

    df.drop(columns=[row_number_col], inplace=True, errors="ignore")

    end_time = time.time()
    time_elapsed = end_time - start_time
    logging.info("Pipeline completed successfully")

    divider()

    logging.info(f"Time elapsed: {round(time_elapsed, 2)} seconds")

    divider()

    if metrics is not None:
        metrics["time_processed_seconds"] = round(time_elapsed, 2)
        metrics["rows_dropped"] = metrics["rows_dropped_nulls"] + metrics["rows_dropped_outliers"]
        metrics["columns_removed"] = (
            metrics["columns_removed_manual"]
            + metrics["columns_removed_empty"]
            + metrics["columns_removed_feature_selection"]
            + metrics["columns_removed_temporal"]
        )

    if output_file:
        export_file(df, output_file)

    if collect_metrics and return_df:
        return df, metrics
    return df if return_df else True
    