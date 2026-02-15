import pandas as pd
from pandas.api.types import is_numeric_dtype
import logging

def clear_null_values(df, threshold):

    if df is None or len(df) == 0:

        logging.info("Dataframe is empty")

        return

    for column in df.columns:

        if (df[column].isnull().sum()) / len(df) > threshold:

            if is_numeric_dtype(df[column]):

                df[column] = df[column].fillna(df[column].mean())

            else:

                mode = df[column].mode(dropna=True)
                fill_value = mode.iloc[0] if not mode.empty else ""
                df[column] = df[column].fillna(fill_value)
        
        else:
            df.dropna(subset=[column], inplace=True)

    return df