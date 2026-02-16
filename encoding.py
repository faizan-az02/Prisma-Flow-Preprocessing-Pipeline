import pandas as pd
import logging
from divider import divider

def encode_features(df, method="onehot", target_col=None, columns=None, exclude_cols=None):

    logging.info(f"=== ENCODING STARTED ===")
    exclude = set(exclude_cols or [])

    # Auto detect categorical columns if not provided
    if columns is None:

        columns = df.select_dtypes(include=["object", "category", "string"]).columns.tolist()
    columns = [c for c in columns if c not in exclude]

    logging.info(f"Columns selected for encoding: {columns}")

    # ---------------- LABEL ENCODING ----------------

    if method.lower() == "label":

        logging.info("Method : Label Encoding")

        from sklearn.preprocessing import LabelEncoder

        le = LabelEncoder()

        for col in columns:
            try:
                df[col] = le.fit_transform(df[col].astype(str))
                logging.info(f'Label encoded column "{col}"')
            except Exception as e:
                logging.warning(f'Failed label encoding column "{col}" | {e}')

    # ---------------- ONE HOT ENCODING ----------------
    elif method.lower() == "onehot":

        logging.info("Method : One-Hot Encoding")

        try:
            df = pd.get_dummies(df, columns=columns, drop_first=False)
            logging.info(f'One-hot encoded columns {columns}')
        except Exception as e:
            logging.error(f'One-hot encoding failed | {e}')

    # ---------------- TARGET ENCODING ----------------
    elif method.lower() == "target":

        logging.info("Method : Target Encoding")

        if target_col is None:
            raise ValueError("target_col must be provided for target encoding")

        for col in columns:
            try:
                means = df.groupby(col)[target_col].mean()
                df[col] = df[col].map(means)
                logging.info(f'Target encoded column "{col}" using target "{target_col}"')
            except Exception as e:
                logging.warning(f'Failed target encoding column "{col}" | {e}')

    else:
        raise ValueError("method must be: 'label', 'onehot', or 'target'")

    logging.info("=== ENCODING COMPLETED ===")

    divider()

    return df
