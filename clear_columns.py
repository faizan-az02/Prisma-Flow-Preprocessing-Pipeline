import pandas as pd
import logging
from divider import divider

# Automatic Removal of Columns

def clear_columns(df, exclude_cols=None, empty_threshold=0.95):

    logging.info(f"=== AUTO REMOVAL OF EMPTY COLUMNS STARTED ===")

    dropped_columns = 0
    exclude = set(exclude_cols or [])
    missing_tokens = {
        "",
        "nan",
        "none",
        "null",
        "na",
        "n/a",
        "nat",
        "missing",
        "nil",
    }

    try:
        empty_threshold = float(empty_threshold)
    except Exception:
        empty_threshold = 0.95
    empty_threshold = max(0.0, min(1.0, empty_threshold))

    n_rows = int(df.shape[0]) if df is not None else 0

    for column in list(df.columns):
        if column in exclude:
            continue

        if n_rows <= 0:
            continue

        s = df[column]
        # Treat NaN and blank strings as "empty"
        empty_mask = s.isna()
        if pd.api.types.is_object_dtype(s) or pd.api.types.is_string_dtype(s):
            norm = s.astype(str).str.strip().str.lower()
            empty_mask = empty_mask | norm.isin(missing_tokens)

        empty_ratio = float(empty_mask.mean())

        if empty_ratio >= empty_threshold:

            logging.info(f'Column "{column}" is empty in {empty_ratio:.1%} rows')

            df.drop(columns=[column], inplace=True)

            dropped_columns += 1

    divider()

    logging.info(f"Total dropped columns: {dropped_columns}")

    logging.info(f"=== AUTO REMOVAL OF EMPTY COLUMNS COMPLETED ===")

    divider()

    return df