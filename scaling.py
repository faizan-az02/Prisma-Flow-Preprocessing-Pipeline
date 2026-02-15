import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import logging
from divider import divider

def scale_features(df, method="standard", columns=None):

    logging.info(f"=== SCALING STARTED")

    # Auto detect numeric columns if not provided
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()

    logging.info(f"Columns selected for scaling: {columns}")

    # Choose scaler
    if method.lower() in ["standard", "zscore"]:
        scaler = StandardScaler()
    elif method.lower() == "minmax":
        scaler = MinMaxScaler()
    else:
        raise ValueError("method must be 'standard', 'zscore', or 'minmax'")

    # Apply scaling
    try:
        df[columns] = scaler.fit_transform(df[columns])
        method_key = str(method).strip().lower()
        method_display = {
            "standard": "Standard",
            "z-score": "Z-score",
            "zscore": "Z-score",
        }.get(method_key, method)
        logging.info(f"Scaled columns using {method_display} Scaler")
    except Exception as e:
        logging.error(f"Scaling failed | {e}")

    logging.info("=== SCALING COMPLETED ===")

    divider()

    return df
