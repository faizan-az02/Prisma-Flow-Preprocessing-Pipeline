import numpy as np
import logging
from divider import divider

# Standard Removal of Outliers

def remove_outliers(
    df,
    drop,
    multiplier=1.5,
    exclude_cols=None,
    method="iqr",
    zscore_threshold=3.0,
    modified_zscore_threshold=3.5,
    return_total=False,
):

    logging.info("=== OUTLIER HANDLING STARTED ===")

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if exclude_cols:
        numeric_cols = [c for c in numeric_cols if c not in set(exclude_cols)]
    total_outliers = 0

    method_key = (method or "iqr").strip().lower()
    if method_key not in {"iqr", "zscore", "modified_zscore"}:
        method_key = "iqr"

    if method_key == "iqr":
        logging.info(f"Method : IQR (multiplier={multiplier})")
    elif method_key == "zscore":
        logging.info(f"Method : Z-Score (threshold={zscore_threshold})")
    else:
        logging.info(f"Method : Modified Z-Score (threshold={modified_zscore_threshold})")

    for col in numeric_cols:
        series = df[col]

        if method_key == "iqr":
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1

            lower_bound = Q1 - multiplier * IQR
            upper_bound = Q3 + multiplier * IQR

            outlier_mask = (series < lower_bound) | (series > upper_bound)

        elif method_key == "zscore":
            mean = series.mean()
            std = series.std(ddof=0)
            if std == 0 or np.isnan(std):
                outlier_mask = np.zeros(len(df), dtype=bool)
            else:
                z = (series - mean) / std
                outlier_mask = z.abs() > float(zscore_threshold)

        else:  # modified_zscore
            median = series.median()
            mad = (series - median).abs().median()
            if mad == 0 or np.isnan(mad):
                outlier_mask = np.zeros(len(df), dtype=bool)
            else:
                mz = 0.6745 * (series - median) / mad
                outlier_mask = mz.abs() > float(modified_zscore_threshold)

        outlier_count = outlier_mask.sum()

        if outlier_count > 0:
            total_outliers += outlier_count

            if drop:
                df = df[~outlier_mask]
                logging.info(f'Removed {outlier_count} outliers from column "{col}"')

            else:
                if method_key == "iqr":
                    df.loc[outlier_mask & (series < lower_bound), col] = lower_bound
                    df.loc[outlier_mask & (series > upper_bound), col] = upper_bound
                    logging.info(f'Capped {outlier_count} outliers in column "{col}"')

                elif method_key == "zscore":
                    if std == 0 or np.isnan(std):
                        logging.info(f'No outliers detected in column "{col}"')
                    else:
                        lower_bound = mean - float(zscore_threshold) * std
                        upper_bound = mean + float(zscore_threshold) * std
                        df.loc[outlier_mask & (series < lower_bound), col] = lower_bound
                        df.loc[outlier_mask & (series > upper_bound), col] = upper_bound
                        logging.info(f'Capped {outlier_count} outliers in column "{col}"')

                else:  # modified_zscore
                    if mad == 0 or np.isnan(mad):
                        logging.info(f'No outliers detected in column "{col}"')
                    else:
                        bound = float(modified_zscore_threshold) * mad / 0.6745
                        lower_bound = median - bound
                        upper_bound = median + bound
                        df.loc[outlier_mask & (series < lower_bound), col] = lower_bound
                        df.loc[outlier_mask & (series > upper_bound), col] = upper_bound
                        logging.info(f'Capped {outlier_count} outliers in column "{col}"')

        else:
            logging.info(f'No outliers detected in column "{col}"')

    divider()

    logging.info(f"Total outliers handled: {total_outliers}")

    logging.info(f"=== OUTLIER HANDLING COMPLETED ===")

    divider()

    if return_total:
        return df, int(total_outliers)
    return df
