import pandas as pd
import numpy as np
from sklearn.feature_selection import VarianceThreshold
import logging
from divider import divider

def feature_selection(df, variance_threshold=0.01, correlation_threshold=0.9):
 
    logging.info("=== FEATURE SELECTION STARTED ===")

    # ---------------- VARIANCE THRESHOLD ----------------
    logging.info("Running Variance Filtering")

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    if len(numeric_cols) == 0:

        logging.warning("No numeric columns found for variance threshold")

    else:

        selector = VarianceThreshold(threshold=variance_threshold)
        selector.fit(df[numeric_cols])

        kept_cols = [col for col, keep in zip(numeric_cols, selector.get_support()) if keep]
        removed_cols = list(set(numeric_cols) - set(kept_cols))

        df = df.drop(columns=removed_cols)

        logging.info(f"Variance Threshold Removed Columns: {removed_cols}")
        logging.info(f"Remaining Columns After Variance Filter: {len(df.columns)}")

    # ---------------- CORRELATION FILTERING ----------------
    logging.info("Running Correlation Filtering")

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    if len(numeric_cols) == 0:
        logging.warning("No numeric columns found for correlation filtering")
    else:
        corr_matrix = df[numeric_cols].corr().abs()

        upper_triangle = corr_matrix.where(
            np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
        )

        to_drop = [
            column for column in upper_triangle.columns
            if any(upper_triangle[column] > correlation_threshold)
        ]

        df = df.drop(columns=to_drop)

        logging.info(f"Correlation Removed Columns: {to_drop}")
        logging.info(f"Remaining Columns After Correlation Filter: {len(df.columns)}")

    logging.info("=== FEATURE SELECTION COMPLETED ===")

    divider()

    return df
