import pandas as pd
import logging
from divider import divider

def export_file(df, filename):

    logging.info(f"=== EXPORT FILE STARTED ===")
    
    df.to_csv(filename, index=False)
    logging.info(f"Processed dataset exported to {filename}")

    logging.info(f"=== EXPORT FILE COMPLETED ===")

    divider()

