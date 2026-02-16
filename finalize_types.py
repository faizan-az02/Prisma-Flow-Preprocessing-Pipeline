import pandas as pd
import logging
from divider import divider
from pandas.api.types import is_object_dtype, is_string_dtype

def finalize_dtypes(df, exclude_cols=None):

    logging.info("=== DTYPE FINALIZATION STARTED ===")
    exclude = set(exclude_cols or [])

    for col in df.columns:
        if col in exclude:
            continue
        original_dtype = df[col].dtype

        # Try numeric conversion
        if is_object_dtype(df[col]) or is_string_dtype(df[col]):
            try:
                converted = pd.to_numeric(df[col])
                df[col] = converted
                logging.info(f'Converted Column "{col}" to {df[col].dtype}')
                continue
            except:
                pass

        # Try datetime conversion
        if is_object_dtype(df[col]) or is_string_dtype(df[col]):
            try:
                converted = pd.to_datetime(df[col], errors="coerce", utc=True, format="ISO8601")

                if converted.notna().sum() > 0:
                    
                    df[col] = converted.dt.tz_convert(None)
                    logging.info(f'Converted column "{col}" to {df[col].dtype}')
                    continue

            except:
                pass

        # Keep remaining text columns as strings
        if is_object_dtype(df[col]) or is_string_dtype(df[col]):
            df[col] = df[col].astype("string")
            logging.info(f'Kept Column "{col}" as {df[col].dtype}')

        if df[col].dtype == original_dtype:
            logging.info(f'Column "{col}" kept as {original_dtype}')

    logging.info("=== DTYPE FINALIZATION COMPLETED ===")

    divider()

    return df
