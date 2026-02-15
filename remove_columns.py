import logging
import pandas as pd
from divider import divider

# Manual Removal of Columns

def remove_columns(df, cols):

    logging.info(f"=== MANUAL REMOVAL OF COLUMNS STARTED ===")

    for col in cols:

        df.drop(columns=[col], inplace=True)

        logging.info(f"Removed column \"{col}\"")

    logging.info(f"=== MANUAL REMOVAL OF COLUMNS COMPLETED ===")

    divider()

    return df

