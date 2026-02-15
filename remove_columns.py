import logging
import pandas as pd
from divider import divider

# Manual Removal of Columns

def remove_columns(df, cols):

    if cols is None:
        return df

    # Normalize input: remove empties/whitespace
    cols = [str(c).strip() for c in cols if str(c).strip()]
    if not cols:
        return df

    logging.info(f"=== MANUAL REMOVAL OF COLUMNS STARTED ===")

    for col in cols:

        if col in df.columns:
            df.drop(columns=[col], inplace=True)
            logging.info(f'Removed column "{col}"')
        else:
            logging.warning(f'Column "{col}" not found, skipping')

    logging.info(f"=== MANUAL REMOVAL OF COLUMNS COMPLETED ===")

    divider()

    return df

