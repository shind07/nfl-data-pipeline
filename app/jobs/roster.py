"""
https://gist.github.com/Deryck97/dff8d33e9f841568201a2a0d5519ac5e
"""
import logging
import os

from app.config import (
    configure_logging,
    DATA_DIRECTORY,
)
from app.utils import (
    download_remote_csv,
    init_directory
)

ROSTER_DIRECTORY = os.path.join(DATA_DIRECTORY, "roster")
REMOTE_ARCHIVE_PATH = 'https://github.com/guga31bb/nflfastR-data/blob/master/roster-data/roster.csv.gz?raw=True'
LOCAL_ARCHIVE_PATH = os.path.join(ROSTER_DIRECTORY, 'roster_archive.csv')
REMOTE_PATH = 'https://github.com/mrcaseb/nflfastR-roster/blob/master/data/nflfastR-roster.csv.gz?raw=True'
LOCAL_PATH = os.path.join(ROSTER_DIRECTORY, 'roster.csv')


def run(backfill: bool = False) -> None:
    """Download NFL rosters CSVs"""
    init_directory(ROSTER_DIRECTORY)

    if backfill:
        logging.info("Backfilling roster data...")
        download_remote_csv(
            remote_path=REMOTE_ARCHIVE_PATH,
            local_path=LOCAL_ARCHIVE_PATH,
            overwrite=True
        )

    logging.info(f"Downloading roster CSV...")
    download_remote_csv(
        remote_path=REMOTE_PATH,
        local_path=LOCAL_PATH,
        overwrite=True
    )


if __name__ == "__main__":
    configure_logging()
    run()
