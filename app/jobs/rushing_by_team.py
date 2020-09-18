"""
Upstream jobs:
- play_by_play
- roster
- rushing_by_player
"""
import logging
import os

import pandas as pd

from app.config import (
    configure_logging,
    CURRENT_YEAR,
    DERIVED_DATA_DIRECTORY
)

from app.transforms import rushing

INPUT_PATH = os.path.join(DERIVED_DATA_DIRECTORY, 'rushing_by_player.csv')
OUTPUT_PATH = os.path.join(DERIVED_DATA_DIRECTORY, 'rushing_by_team.csv')


def _extract(window: str, path: str = INPUT_PATH, ) -> pd.DataFrame:
    path = path.replace('.csv', f"_by_{window}.csv")
    return pd.read_csv(path, low_memory=False)


def _transform(df_player_rushing: pd.DataFrame, window: str) -> pd.DataFrame:
    return rushing.get_team_stats(df_player_rushing, window)


def _load(df: pd.DataFrame, window: str, path: str = OUTPUT_PATH) -> None:
    path = path.replace(".csv", f"_by_{window}.csv")
    logging.info(f"Writing {len(df)} rows to {path}...")
    df.to_csv(path, index=False)


def _run(window: str) -> None:
    df_player_rushing = _extract(window)
    df_team_rushing = _transform(df_player_rushing, window)
    _load(df_team_rushing, window)


def run(season: int = CURRENT_YEAR):
    logging.info("Grabbing team rushing stats by year...")
    _run("year")

    logging.info("Grabbing team rushing stats by week...")
    _run("week")


if __name__ == "__main__":
    configure_logging()
    run()
