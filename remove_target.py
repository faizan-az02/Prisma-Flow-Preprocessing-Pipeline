import logging
from divider import divider

def remove_target(df, target_col=None):

    if target_col is None:

        return df, None

    logging.info(f"=== REMOVING TARGET COLUMN STARTED ===")

    if target_col not in df.columns:

        raise ValueError(f"Target column '{target_col}' not found in dataframe.")
    
    y = df[target_col].copy()
    X = df.drop(columns=[target_col])

    logging.info(f"=== REMOVING TARGET COLUMN COMPLETED ===")

    divider()
    
    return X, y
