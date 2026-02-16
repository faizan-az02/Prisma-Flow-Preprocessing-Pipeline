import pandas as pd
from pandas.api.types import is_numeric_dtype
import logging
from divider import divider

# Automatic Removal of Null Values

def clear_null_values(df, threshold, exclude_cols=None):

    logging.info(f"=== AUTO REMOVAL OF NULL VALUES STARTED ===")

    total_dropped_rows = 0
    exclude = set(exclude_cols or [])

    if df is None or len(df) == 0:

        logging.info("Dataframe is empty")

        return df

    for column in df.columns:
        if column in exclude:
            continue

        if (df[column].isnull().sum()) / len(df) > threshold:

            if is_numeric_dtype(df[column]):

                df[column] = df[column].fillna(df[column].mean())

                logging.info(f"Filled with the mean - {df[column].mean().round(2)} of the column \"{column}\"")

            else:

                mode = df[column].mode(dropna=True)
                fill_value = mode.iloc[0] if not mode.empty else ""
                df[column] = df[column].fillna(fill_value)

                logging.info(f"Filled with the mode - {fill_value} of the column \"{column}\"")
        
        else:

            rows_before = len(df)
            df.dropna(subset=[column], inplace=True)
            rows_after = len(df)
            dropped_rows = rows_before - rows_after
            logging.info(f"Dropped {dropped_rows} rows with nulls from the column \"{column}\"")

            total_dropped_rows += dropped_rows

    divider()

    logging.info(f"Total dropped rows: {total_dropped_rows}")

    logging.info(f"=== AUTO REMOVAL OF NULL VALUES COMPLETED ===")

    divider()

    return df