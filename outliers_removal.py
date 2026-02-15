import numpy as np
import logging

def remove_outliers(df, multiplier=1.5, drop=True):

    logging.info("=== OUTLIER HANDLING STARTED ===")

    numeric_cols = df.select_dtypes(include=[np.number]).columns
    total_outliers = 0

    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR

        outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
        outlier_count = outlier_mask.sum()

        if outlier_count > 0:
            total_outliers += outlier_count

            if drop:
                df = df[~outlier_mask]
                logging.info(f'Removed {outlier_count} outliers from column "{col}"')

            else:
                df[col] = np.where(df[col] < lower_bound, lower_bound, df[col])
                df[col] = np.where(df[col] > upper_bound, upper_bound, df[col])
                logging.info(f'Capped {outlier_count} outliers in column "{col}"')

        else:
            logging.info(f'No outliers detected in column "{col}"')

    logging.info(f"Total outliers handled: {total_outliers}")
    logging.info("=== OUTLIER HANDLING COMPLETED ===")

    divider()

    return df
