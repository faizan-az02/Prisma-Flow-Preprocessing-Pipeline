import pandas as pd
import logging
from divider import divider

def clear_columns(df):

    dropped_columns = 0

    for column in df.columns:

        if df[column].isna().all():

            logging.info(f"Column \"{column}\" is empty")

            df.drop(columns=[column], inplace=True)

            dropped_columns += 1

    divider()

    logging.info(f"Total dropped columns: {dropped_columns}")

    divider()

    return df