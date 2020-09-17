import logging
import os


APP_NAME = "app"
DATA_DIRECTORY = "data"
CURRENT_YEAR = 2020

GAMES_DIRECTORY = os.path.join(DATA_DIRECTORY, "games")
PLAY_BY_PLAY_DIRECTORY = os.path.join(DATA_DIRECTORY, "play_by_play")
ROSTER_DIRECTORY = os.path.join(DATA_DIRECTORY, "roster")

DB_NAME = 'nfl.db'
DB_PATH = os.path.join(DATA_DIRECTORY, DB_NAME)


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s -  %(levelname)s - {%(filename)s:%(lineno)d} - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
