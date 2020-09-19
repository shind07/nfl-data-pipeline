"""
Upstream jobs:
- play_by_play
- roster
"""
import logging

import numpy as np
import pandas as pd

from app.config import (
    configure_logging,
    CURRENT_YEAR,
)
from app.utils import (
    get_window_columns,
    extract_play_by_play,
    extract_roster,
    float_to_int,
)
from app.transforms import rushing

OUTPUT_PATH = 'data/derived/rushing_by_{level}_by_{window}.csv'
RUSHING_COLUMNS_TO_KEEP = ['year', 'player_id', 'player', 'rush', 'yards_gained_designed',
                           'rush_touchdown_designed', 'fumble_designed', 'fumble_lost_designed',
                           'fumble_out_of_bounds_designed', 'pass',
                           'yards_gained_scrambles', 'rush_touchdown_scrambles',
                           'fumble_scrambles', 'fumble_lost_scrambles',
                           'fumble_out_of_bounds_scrambles', 'qb_kneel', 'yards_gained'
                           ]


def _extract() -> pd.DataFrame:
    return extract_play_by_play(), extract_roster()


def _transform_by_week(df_play_by_play: pd.DataFrame, df_roster: pd.DataFrame, year: int = CURRENT_YEAR) -> pd.DataFrame:
    """
    Get all the weekly stats for each player.
    The weekly stats can then be rolled up to team stats and/or yearly stats.
    """
    logging.info(f"Grabbing rushing play by play data...")
    df_rushing_plays = rushing.get_rushing_plays(df_play_by_play)
    window = 'week'
    window_columns = get_window_columns(window)

    logging.info("Loading designed, scramble, and kneel rushing data...")
    df_rushing_designed = rushing.get_designed_rushing_stats(df_rushing_plays, window)
    df_rushing_scrambles = rushing.get_scramble_rushing_stats(df_rushing_plays, window)
    df_rushing_qb_kneels = rushing.get_qb_kneel_stats(df_rushing_plays, window)

    logging.info(f"Joining scrambles to designed rushing stats...")
    df_rushing_all = df_rushing_designed.merge(
        df_rushing_scrambles,
        how='outer',
        left_on=["rusher_id"] + window_columns,
        right_on=['passer_id'] + window_columns,
        suffixes=['_designed', '_scrambles']
    )
    df_rushing_all['player'] = np.where(df_rushing_all['rusher'].isna(), df_rushing_all['passer'], df_rushing_all['rusher'])
    df_rushing_all['player_id'] = np.where(df_rushing_all['rusher_id'].isna(), df_rushing_all['passer_id'], df_rushing_all['rusher_id'])
    assert sum(df_rushing_all['player'].isna()) == 0
    assert sum(df_rushing_all['player_id'].isna()) == 0

    logging.info(f"Joining QB kneels to rushing stats...")
    df_rushing_all = df_rushing_all.merge(
        df_rushing_qb_kneels,
        how='outer',
        left_on=["player_id"] + window_columns,
        right_on=['rusher_id'] + window_columns,
        suffixes=['', '_kneel']
    )
    df_rushing_all['player'] = np.where(df_rushing_all['player'].isna(), df_rushing_all['rusher_kneel'], df_rushing_all['player'])
    df_rushing_all['player_id'] = np.where(df_rushing_all['player_id'].isna(), df_rushing_all['rusher_id_kneel'], df_rushing_all['player_id'])
    assert sum(df_rushing_all['player'].isna()) == 0
    assert sum(df_rushing_all['player_id'].isna()) == 0

    # Clean up the DataFrame
    df_rushing_all.fillna(0, inplace=True)
    df_rushing_all = df_rushing_all.apply(float_to_int)
    keeper_columns = RUSHING_COLUMNS_TO_KEEP if window == 'year' else ['week'] + RUSHING_COLUMNS_TO_KEEP
    df_rushing_all = df_rushing_all.loc[:, keeper_columns]

    logging.info(f"Joining roster data to rushing stats...")
    df_roster_year = df_roster.loc[df_roster['team_season'] == year]
    df_roster_year = df_roster_year.rename(columns={
        'pbp_name': 'rusher',
        'teamPlayers_position': 'pos',
        'team_abbr': 'team'
    })

    roster_columns = ['team', 'pos', 'pbp_id']
    df_rushing_all = df_rushing_all.merge(df_roster_year[roster_columns], how='left', left_on='player_id', right_on='pbp_id')
    assert(sum(df_rushing_all['pos'].isna()) == 0)

    df_rushing_all = df_rushing_all.rename(columns={
        'qb_kneel': 'qb_kneels',
        'yards_gained': 'qb_kneel_yards',
        'pass': 'scrambles',
        'rush_touchdown_scrambles': 'scramble_touchdowns',
        'yards_gained_scrambles': 'scramble_yards'
    })

    logging.info("Computing rushing stats...")
    df_rushing_all['total_yards'] = df_rushing_all['yards_gained_designed'] + \
        df_rushing_all['scramble_yards'] + df_rushing_all['qb_kneel_yards']

    df_rushing_all['total_attempts'] = df_rushing_all['rush'] + \
        df_rushing_all['scrambles'] + df_rushing_all['qb_kneels']

    df_rushing_all['total_touchdowns'] = df_rushing_all['rush_touchdown_designed'] + \
        df_rushing_all['scramble_touchdowns']

    df_rushing_all['total_fumbles'] = df_rushing_all['fumble_designed'] + \
        df_rushing_all['fumble_scrambles']

    df_rushing_all['total_fumbles_lost'] = df_rushing_all['fumble_lost_designed'] + \
        df_rushing_all['fumble_lost_scrambles']

    df_rushing_all['total_fumbles_out_of_bounds'] = df_rushing_all['fumble_out_of_bounds_designed'] + \
        df_rushing_all['fumble_out_of_bounds_scrambles']

    return df_rushing_all.drop("pbp_id", axis=1)


def _transform_by_week_team(df_weekly_player_stats: pd.DataFrame) -> pd.DataFrame:
    """Aggregate player stats to the team level."""
    logging.info("Aggregating weekly player stats to the team level...")
    grouping_columns = ['year', 'team', 'week']
    return df_weekly_player_stats.groupby(grouping_columns, as_index=False).sum()


def _transform_by_year(df_weekly_stats: pd.DataFrame, level: str) -> pd.DataFrame:
    """Aggregate weekly stats for the year."""
    logging.info(f"Aggregating weekly {level} stats by the year...")
    if level not in ('player', 'team'):
        raise ValueError(f"Given level: {level} in one of player or team.")

    grouping_columns = {
        'player': ['year', 'team', 'pos', 'player_id', 'player'],
        'team': ['year', 'team'],
    }
    df_weekly_stats['games'] = 1
    return df_weekly_stats.groupby(grouping_columns[level], as_index=False).sum()


def _add_team_stats(df_player_stats: pd.DataFrame, df_team_stats: pd.DataFrame) -> pd.DataFrame:
    """Add the team totals to the player stats"""
    logging.info('Enriching player stats with team stats...')
    df_team_stats = df_team_stats.rename(columns={
        column: "team_" + column for column in df_team_stats if column not in ('team', 'week')
    })
    df_player_stats = df_player_stats.merge(df_team_stats, how='left', on=['team', 'week'])

    df_player_stats['%_team_carries'] = df_player_stats['rush'] / df_player_stats['team_rush']
    df_player_stats['%_team_yards'] = df_player_stats['yards_gained_designed'] / df_player_stats['team_yards_gained_designed']

    return df_player_stats


def _load(df: pd.DataFrame, path: str = OUTPUT_PATH) -> None:
    logging.info(f"Writing {len(df)} rows to {path}...")
    df.to_csv(path, index=False)


def run() -> None:
    df_play_by_play, df_roster = _extract()

    df_rushing_by_player_by_week = _transform_by_week(df_play_by_play, df_roster)
    df_rushing_by_team_by_week = _transform_by_week_team(df_rushing_by_player_by_week)
    df_rushing_by_player_by_week = _add_team_stats(df_rushing_by_player_by_week, df_rushing_by_team_by_week)

    df_rushing_by_player_by_year = _transform_by_year(df_rushing_by_player_by_week, 'player')
    _load(df_rushing_by_player_by_week, OUTPUT_PATH.format(level='player', window='week'))
    _load(df_rushing_by_player_by_year, OUTPUT_PATH.format(level='player', window='years'))

    df_rushing_by_team_by_week = _transform_by_week_team(df_rushing_by_player_by_week)
    df_rushing_by_team_by_year = _transform_by_year(df_rushing_by_team_by_week, 'team')
    _load(df_rushing_by_team_by_week, OUTPUT_PATH.format(level='team', window='week'))
    _load(df_rushing_by_team_by_year, OUTPUT_PATH.format(level='team', window='year'))


if __name__ == "__main__":
    configure_logging()
    run()
