"""
https://gist.github.com/Deryck97/dff8d33e9f841568201a2a0d5519ac5e

"""
import logging
import os

from app.config import (
    configure_logging,
    DATA_DIRECTORY,
)
from app.utils import download_remote_csv

ROSTER_DIRECTORY = os.path.join(DATA_DIRECTORY, "roster")
REMOTE_PATH = 'https://github.com/guga31bb/nflfastR-data/blob/master/roster-data/roster.csv.gz?raw=True'
LOCAL_PATH = os.path.join(ROSTER_DIRECTORY, 'roster.csv')


def run():
    """Download NFL rosters - all in a single CSV"""
    logging.info(f"Downloading roster CSV...")
    if not os.path.exists(ROSTER_DIRECTORY):
        logging.info(f"{ROSTER_DIRECTORY} does not exist - creating...")
        os.mkdir(ROSTER_DIRECTORY)

    download_remote_csv(
        remote_path=REMOTE_PATH,
        local_path=LOCAL_PATH,
        overwrite=True
    )


if __name__ == "__main__":
    configure_logging()
    run()
