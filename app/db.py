import os
import sqlite3

import pandas as pd

from app.config import DB_PATH


def get_db_conn(db_path: str = DB_PATH) -> sqlite3.Connection:
    return sqlite3.connect(db_path)


def drop_db(db_path: str = DB_PATH) -> None:
    """Delete the database, as it if were a file."""
    logging.info(f"Deleting database: {db_path}")
    os.remove(db_path)
    

