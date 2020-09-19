import pandas as pd

from app.utils import get_window_columns

BASE_RUSHING_COLUMNS = ["yards_gained", "rush_touchdown", "fumble", "fumble_lost", "fumble_out_of_bounds"]


def get_rushing_plays(df_play_by_play: pd.DataFrame) -> pd.DataFrame:
    """Including QB kneels b/c they count as rushing stats."""
    return df_play_by_play.loc[
        df_play_by_play['play_type'].isin(['run', 'qb_kneel'])
        & (df_play_by_play['sack'] == 0)
        & (df_play_by_play["two_point_attempt"] == 0)
    ]


def get_designed_rushing_stats(df_rushing_plays: pd.DataFrame, window: str) -> pd.DataFrame:
    """
    Designed rushing plays will have a "rusher" value.
    We filter out QB kneels here.
    """
    window_columns = get_window_columns(window)
    grouping_columns = window_columns + ["rusher_id", "rusher"]
    filter_columns = grouping_columns + BASE_RUSHING_COLUMNS + ['rush']
    mask = df_rushing_plays['play_type'] != 'qb_kneel'
    return df_rushing_plays[mask][filter_columns].groupby(grouping_columns, as_index=False).sum()


def get_scramble_rushing_stats(df_rushing_plays: pd.DataFrame, window: str) -> pd.DataFrame:
    """
    Scramble rushing plays will have a "passer" value.
    We filter out QB kneels here.
    """
    window_columns = get_window_columns(window)
    grouping_columns = window_columns + ["passer_id", "passer"]
    filter_columns = grouping_columns + BASE_RUSHING_COLUMNS + ['pass']
    mask = df_rushing_plays['play_type'] != 'qb_kneel'
    return df_rushing_plays[mask][filter_columns].groupby(grouping_columns, as_index=False).sum()


def get_qb_kneel_stats(df_rushing_plays: pd.DataFrame, window: str) -> pd.DataFrame:
    """QB kneels count as rushing years so we need to handle them"""
    window_columns = get_window_columns(window)
    grouping_columns = window_columns + ["rusher_id", "rusher"]
    filter_columns = grouping_columns + ["qb_kneel", "yards_gained"]
    mask = df_rushing_plays['play_type'] == 'qb_kneel'
    return df_rushing_plays[mask][filter_columns].groupby(grouping_columns, as_index=False).sum()


def get_team_stats(df_player_rushing: pd.DataFrame, window: str) -> pd.DataFrame:
    """Aggregate the player data to the team level."""
    window_columns = get_window_columns(window)
    df_team_rushing = df_player_rushing.groupby(['team'] + window_columns, as_index=False).sum()
    df_team_rushing = df_team_rushing.rename(columns={
        col: 'team_' + col for col in df_team_rushing.columns if col != 'team'
    })
    return df_team_rushing
