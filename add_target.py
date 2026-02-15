import logging
from divider import divider
import pandas as pd

def add_target(df_features, target_series, target_col_name="target"):

    if target_series is None:
        
        return df_features

    logging.info(f"=== ADDING TARGET COLUMN STARTED ===")

    df_combined = df_features.copy()
    df_combined[target_col_name] = target_series.values

    logging.info(f"=== ADDING TARGET COLUMN COMPLETED ===")

    divider()

    return df_combined
