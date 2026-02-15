import logging
import pandas as pd
from divider import divider

# Manual Removal of Columns

def remove_columns(df, cols):

    for col in cols:

        df.drop(columns=[col], inplace=True)

        logging.info(f"Removed column \"{col}\"")

    divider()

    return df

