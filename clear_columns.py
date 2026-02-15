import pandas as pd
import logging

def clear_columns(df):

    for column in df.columns:

        if df[column].isna().all():

            logging.info(f"Column {column} is empty")

            df.drop(columns=[column], inplace=True)

    return df