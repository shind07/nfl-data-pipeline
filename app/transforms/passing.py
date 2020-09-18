

def get_sack_yards():
    df_sack_pbp = df.loc[
        (df['play_type'] == 'pass')
        & (df['sack'] == 1)
        & (df["two_point_attempt"] == 0) 
    ]
    cols = ["year", "week","passer_id", "passer", "sack", "yards_gained"]

    df_rush_stats_sacks = df_sack_pbp[cols].groupby(["year", "week","passer_id", "passer"], as_index=False).sum()
    df_rush_stats_sacks.sort_values("yards_gained", ascending=False)