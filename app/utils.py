import logging
import os

import pandas as pd


def download_remote_csv(remote_path: str, local_path: str, overwrite: bool = False) -> None:
    """Download a remote csv to the local filesystem."""
    if os.path.exists(local_path):
        if overwrite:
            logging.info(f"Overwriting {local_path}...")
        else:
            logging.info(f"{local_path} exists - skipping download.")
            return

    logging.info(f"Downloading {remote_path} to {local_path}...")
    df = pd.read_csv(
        remote_path,
        compression='gzip' if "csv.gz" in remote_path else "infer",
        low_memory=False
    )
    df.to_csv(local_path, index=False)
    logging.info(f"Downloaded data ({len(df)} rows) to {local_path}")


def _atomic_csv_rewrite(df: pd.DataFrame, local_path: str) -> None:
    """Wait until the csv write is confirmed before deleting old file"""
    temp_path = local_path.replace(".csv", "_temp.csv")
    os.rename(local_path, temp_path)
    df.to_csv(local_path, index=False)
    os.remove(temp_path)
