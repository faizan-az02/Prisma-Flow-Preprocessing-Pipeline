import logging
from divider import divider
import pandas as pd

def add_target(df_features, target_series, target_col_name="target", key_col=None):

    if target_series is None:

        return df_features

    logging.info(f"=== ADDING TARGET COLUMN STARTED ===")

    df_combined = df_features.merge(
        target_series[[key_col, target_col_name]],
        on=key_col,
        how="left",
        validate="one_to_one",
    ).drop(columns=[key_col])

    logging.info(f"=== ADDING TARGET COLUMN COMPLETED ===")

    divider()

    return df_combined
