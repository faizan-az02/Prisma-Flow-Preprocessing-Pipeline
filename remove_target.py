import logging
from divider import divider

def remove_target(df, target_col=None, id_col=None):

    if target_col is None:

        return df, None

    logging.info(f"=== REMOVING TARGET COLUMN STARTED ===")

    if target_col not in df.columns:

        raise ValueError(f"Target column '{target_col}' not found in dataframe.")
    
    if id_col is not None and id_col in df.columns:
        # Keep an explicit ID so target can be re-attached after row drops.
        y = df[[id_col, target_col]].copy()
    else:
        y = df[target_col].copy()
    X = df.drop(columns=[target_col])

    logging.info(f"=== REMOVING TARGET COLUMN COMPLETED ===")

    divider()
    
    return X, y
