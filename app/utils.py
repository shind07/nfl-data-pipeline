import logging
import os

import numpy as np
import pandas as pd

from app.config import (
    CURRENT_YEAR,
    PLAY_BY_PLAY_DIRECTORY,
    ROSTER_DIRECTORY,
)


def extract_play_by_play(year: int = CURRENT_YEAR) -> pd.DataFrame:
    path = os.path.join(PLAY_BY_PLAY_DIRECTORY, f"{year}.csv")
    df = pd.read_csv(path, low_memory=False)
    df['year'] = year
    return df


def extract_roster() -> pd.DataFrame:
    df_roster = pd.read_csv(os.path.join(ROSTER_DIRECTORY, 'roster.csv'), low_memory=False)
    df_roster.columns = [col.replace(".", '_') for col in df_roster.columns]
    return df_roster


def get_window_columns(window: str) -> list:
    if window not in ('year', 'week'):
        raise ValueError(f"Cannot group by window: {window}")
    return ['year'] if window == 'year' else ['year', 'week']


def float_to_int(column):
    """Turn all float columns into integers. Used with df.apply(float_to_int)"""
    return np.int64(column) if column.dtype == np.float64 else column


def init_directory(path: str) -> None:
    """Create directory if not exists"""
    if not os.path.exists(path):
        logging.info(f"{path} directory doesn't exist - creating...")
        os.mkdir(path)


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
    _atomic_csv_rewrite(df, local_path)
    logging.info(f"Downloaded data ({len(df)} rows) to {local_path}")


def _atomic_csv_rewrite(df: pd.DataFrame, local_path: str) -> None:
    """Wait until the csv write is confirmed before deleting old file"""
    temp_path = local_path.replace(".csv", "_temp.csv")
    if os.path.exists(local_path):
        os.rename(local_path, temp_path)

    df.to_csv(local_path, index=False)

    if os.path.exists(temp_path):
        os.remove(temp_path)


def merge_csvs(csv_paths: list, output_path: str) -> None:
    """Merge all CSVs into a single file"""
    logging.info(f"Merging {len(csv_paths)} files...")

    df_all = pd.DataFrame()

    for path in csv_paths:
        df_temp = pd.read_csv(path, low_memory=False)
        logging.info(f"Appending {len(df_temp)} rows from {path}...")
        df_all = df_all.append(df_temp, sort=True)

    logging.info(f"Writing {len(df_all)} rows to {output_path}...")
    df_all.to_csv(output_path, index=False)
