import logging
from divider import divider
import pandas as pd

def add_target(df_features, target_series, target_col_name="target", key_col=None):

    if target_series is None:
        
        return df_features

    logging.info(f"=== ADDING TARGET COLUMN STARTED ===")

    df_combined = df_features.copy()

    # Preferred: join by an explicit key column (e.g., row_number).
    if key_col is not None and isinstance(target_series, pd.DataFrame):
        if key_col not in df_combined.columns:
            raise ValueError(f'Key column "{key_col}" not found in features dataframe.')
        if key_col not in target_series.columns:
            raise ValueError(f'Key column "{key_col}" not found in target dataframe.')
        if target_col_name not in target_series.columns:
            raise ValueError(f'Target column "{target_col_name}" not found in target dataframe.')

        df_combined = df_combined.merge(
            target_series[[key_col, target_col_name]],
            on=key_col,
            how="left",
            validate="one_to_one",
        )
    # Fallback: align by index (works as long as index is stable).
    elif isinstance(target_series, pd.Series):
        df_combined[target_col_name] = target_series.reindex(df_combined.index)
    else:
        if len(target_series) != len(df_combined):
            raise ValueError(
                f"Target length ({len(target_series)}) does not match features length ({len(df_combined)}). "
                "Pass a pandas Series with the original index or a DataFrame with a join key."
            )
        df_combined[target_col_name] = target_series

    # If we used a key column for alignment, drop it from the final output.
    if key_col is not None and key_col in df_combined.columns:
        df_combined.drop(columns=[key_col], inplace=True)

    logging.info(f"=== ADDING TARGET COLUMN COMPLETED ===")

    divider()

    return df_combined
