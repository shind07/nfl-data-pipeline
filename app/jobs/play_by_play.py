"""
https://gist.github.com/Deryck97/dff8d33e9f841568201a2a0d5519ac5e

"""
import logging
import os

import pandas as pd

from app.config import (
    configure_logging,
    CURRENT_YEAR,
    DATA_DIRECTORY,
)
from app.utils import download_remote_csv

PLAY_BY_PLAY_DIRECTORY = os.path.join(DATA_DIRECTORY, "play_by_play")
REMOTE_PATH_TEMPLATE = 'https://github.com/guga31bb/nflfastR-data/blob/master/data/play_by_play_{year}.csv.gz?raw=True'
LOCAL_PATH_TEMPLATE = "{directory}/{year}.csv"
BACKFILL_YEARS = [year for year in range(1999, CURRENT_YEAR)]


def backfill():
    """Download previous CSVs if they don't exist"""
    logging.info("Backfilling play by play data...")
    if not os.path.exists(PLAY_BY_PLAY_DIRECTORY):
        logging.info(f"{PLAY_BY_PLAY_DIRECTORY} directory doesn't exist - creating...")
        os.mkdir(PLAY_BY_PLAY_DIRECTORY)

    for year in BACKFILL_YEARS:
        download_remote_csv(
            remote_path=REMOTE_PATH_TEMPLATE.format(year=year),
            local_path=LOCAL_PATH_TEMPLATE.format(directory=PLAY_BY_PLAY_DIRECTORY, year=year),
            overwrite=False
        )


def merge(start_year: int = 1999, end_year: int = 2020):
    """Merge all the yearly CSVs into a single file"""
    logging.info("Merging yearly play_by_play CSVs...")

    df_all_years = pd.DataFrame()

    for year in range(start_year, end_year + 1):
        path = LOCAL_PATH_TEMPLATE.format(
            directory=PLAY_BY_PLAY_DIRECTORY,
            year=year
        )
        df_year = pd.read_csv(path, low_memory=False)
        df_year['year'] = year
        logging.info(f"Appending {len(df_year)} rows from {path}...")
        df_all_years = df_all_years.append(df_year, sort=True)

    output_path = LOCAL_PATH_TEMPLATE.format(directory=PLAY_BY_PLAY_DIRECTORY, year="all")
    logging.info(f"Writing {len(df_all_years)} rows to {output_path}...")
    df_all_years.to_csv(output_path, index=False)


def run():
    """Backfill old data, re-download the 2020 CSV, merge all data together."""
    backfill()
    logging.info(f"Downloading play by play for {CURRENT_YEAR}...")
    download_remote_csv(
        remote_path=REMOTE_PATH_TEMPLATE.format(year=CURRENT_YEAR),
        local_path=LOCAL_PATH_TEMPLATE.format(directory=PLAY_BY_PLAY_DIRECTORY, year=CURRENT_YEAR),
        overwrite=True
    )
    merge()


if __name__ == "__main__":
    configure_logging()
    run()
