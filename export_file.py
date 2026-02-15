import pandas as pd
import logging
from divider import divider

def export_file(df, filename):

    logging.info(f"=== EXPORT FILE STARTED ===")
    
    df.to_csv("processed_dataset.csv", index=False)
    logging.info("Processed dataset exported to processed_dataset.csv")

    logging.info(f"=== EXPORT FILE COMPLETED ===")

    divider()

