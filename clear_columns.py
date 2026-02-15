import pandas as pd
import logging
from divider import divider

# Automatic Removal of Columns

def clear_columns(df):

    logging.info(f"=== AUTO REMOVAL OF EMPTY COLUMNS STARTED ===")

    dropped_columns = 0

    for column in df.columns:

        if df[column].isna().all():

            logging.info(f"Column \"{column}\" is empty")

            df.drop(columns=[column], inplace=True)

            dropped_columns += 1

    divider()

    logging.info(f"Total dropped columns: {dropped_columns}")

    logging.info(f"=== AUTO REMOVAL OF EMPTY COLUMNS COMPLETED ===")

    divider()

    return df