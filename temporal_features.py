import pandas as pd
import logging
from divider import divider

def extract_temporal_features(df, drop_original=True, exclude_cols=None):
    """
    Extract temporal features from datetime64 columns and time-only columns.
    
    datetime64 columns:
        - year, month, day, hour, minute, second, weekday
        - optional Unix timestamp
    
    time-only columns (HH:MM:SS string):
        - hour, minute, second
    
    Parameters:
    df : pandas DataFrame
    drop_original : bool
        Whether to drop the original columns
    add_timestamp : bool
        Whether to add Unix timestamp for datetime64 columns
    """
    
    logging.info("=== TEMPORAL FEATURE EXTRACTION STARTED ===")
    exclude = set(exclude_cols or [])
    
    # ---------------- DATETIME64 COLUMNS ----------------
    datetime_cols = [c for c in df.select_dtypes(include=["datetime64[ns]"]).columns.tolist() if c not in exclude]
    
    if datetime_cols:
        logging.info(f"Detected Date-Time columns: {datetime_cols}")
        for col in datetime_cols:
            df[f"{col}_year"] = df[col].dt.year
            df[f"{col}_month"] = df[col].dt.month
            df[f"{col}_day"] = df[col].dt.day
            df[f"{col}_hour"] = df[col].dt.hour
            df[f"{col}_minute"] = df[col].dt.minute
            df[f"{col}_second"] = df[col].dt.second
            df[f"{col}_weekday"] = df[col].dt.weekday

            logging.info(f"Extracted features from {col}: Year, Month, Day, Hour, Minute, Second, Weekday")
            
            if drop_original:
                df = df.drop(columns=[col])
                logging.info(f"Dropped Original Column: {col}")
    else:
        logging.info("No Date-Time columns detected.")
    
    # ---------------- TIME-ONLY COLUMNS ----------------
    time_cols = []
    for col in df.select_dtypes(include=["object"]).columns:
        if col in exclude:
            continue
        try:
            pd.to_datetime(df[col], format="%H:%M:%S", errors="raise")
            time_cols.append(col)
        except:
            continue
    
    if time_cols:
        logging.info(f"Detected Time-Only columns: {time_cols}")
        for col in time_cols:
            times = pd.to_datetime(df[col], format="%H:%M:%S")
            df[f"{col}_hour"] = times.dt.hour
            df[f"{col}_minute"] = times.dt.minute
            df[f"{col}_second"] = times.dt.second
            
            logging.info(f"Extracted features from {col}: Hour, Minute, Second")
            
            if drop_original:
                df = df.drop(columns=[col])
                logging.info(f"Dropped Original Column: {col}")
    else:
        logging.info("No Time-Only columns detected.")
    
    logging.info("=== TEMPORAL FEATURE EXTRACTION COMPLETED ===")
    divider()
    
    return df
