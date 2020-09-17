"""
https://gist.github.com/Deryck97/dff8d33e9f841568201a2a0d5519ac5e

"""
import logging
import os

import pandas as pd

from app.db import (
    drop_table,
    get_db_conn
)
from app.config import (
    configure_logging,
    CURRENT_YEAR,
    DATA_DIRECTORY,
)
from app.utils import (
    download_remote_csv,
    init_directory,
    merge_csvs
)

PLAY_BY_PLAY_DIRECTORY = os.path.join(DATA_DIRECTORY, "play_by_play")
REMOTE_PATH_TEMPLATE = 'https://github.com/guga31bb/nflfastR-data/blob/master/data/play_by_play_{year}.csv.gz?raw=True'
LOCAL_PATH_TEMPLATE = "{directory}/{year}.csv"
ARCHIVE_CSV_PATH = os.path.join(PLAY_BY_PLAY_DIRECTORY, f"1999_{CURRENT_YEAR - 1}.csv")


def download_archives() -> None:
    """Download previous CSVs if they don't exist"""
    logging.info("Backfilling play by play data...")
    for year in range(1999, CURRENT_YEAR):
        download_remote_csv(
            remote_path=REMOTE_PATH_TEMPLATE.format(year=year),
            local_path=LOCAL_PATH_TEMPLATE.format(directory=PLAY_BY_PLAY_DIRECTORY, year=year),
            overwrite=False
        )


def load_to_db(path: str) -> None:
    db_conn = get_db_conn()
    cur = db_conn.cursor()
    query = """
        DELETE FROM play_by_play
        WHERE year = {year}
    """


def run(backfill: bool = False) -> None:
    """Backfill old data, re-download the 2020 CSV, merge all data together."""
    init_directory(PLAY_BY_PLAY_DIRECTORY)

    if backfill:
        download_archives()
        historic_csvs = [
            os.path.join(PLAY_BY_PLAY_DIRECTORY, f)
            for f in os.listdir(PLAY_BY_PLAY_DIRECTORY)
            if int(f.split('.')[0]) < CURRENT_YEAR
        ]
        merge_csvs(historic_csvs, ARCHIVE_CSV_PATH)

    logging.info(f"Downloading play by play for {CURRENT_YEAR}...")
    current_local_path = LOCAL_PATH_TEMPLATE.format(directory=PLAY_BY_PLAY_DIRECTORY, year=CURRENT_YEAR)
    download_remote_csv(
        remote_path=REMOTE_PATH_TEMPLATE.format(year=CURRENT_YEAR),
        local_path=current_local_path,
        overwrite=True
    )

    logging.info("Merging current year data with archives...")
    all_local_path = LOCAL_PATH_TEMPLATE.format(directory=PLAY_BY_PLAY_DIRECTORY, year="all")
    merge_csvs([ARCHIVE_CSV_PATH, current_local_path], all_local_path)

    load_csv_to_db(current_local_path)

if __name__ == "__main__":
    configure_logging()
    run()
