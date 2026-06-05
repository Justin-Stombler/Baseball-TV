import pandas as pd
import pybaseball



def get_hitter_expected_stats(year: int, min_pa: str = "q") -> pd.DataFrame:
    """
    Fetch pre-aggregated expected stats for all hitters in a given year.
    
    ARGUMENTS
        year: The year for which you wish to retrieve expected stats. Format: YYYY.
        min_pa: Minimum plate appearances. "q" = qualified, or specify a number like 100.
    
    Returns DataFrame with columns like: xBA, xSLG, xwOBA, exit_velocity, etc.
    """
    return pybaseball.statcast_batter_expected_stats(year, minPA=min_pa)


def get_pitcher_expected_stats(year: int, min_ip: str = "q") -> pd.DataFrame:
    """
    Fetch pre-aggregated expected stats for all pitchers in a given year.
    
    ARGUMENTS
        year: The year for which you wish to retrieve expected stats. Format: YYYY.
        min_ip: Minimum plate appearances for opposing batters. "q" = qualified, or specify a number.
    
    Returns DataFrame with columns like: xBA, xwOBA, xERA, etc.
    """
    return pybaseball.statcast_pitcher_expected_stats(year, minPA=min_ip)



def get_batter_exitvelo_barrels(year: int, min_bbe: str = "q") -> pd.DataFrame:
    """
    Fetch batted ball exit velo and barrel data for all batters in a given year.
    
    ARGUMENTS
        year: The year for which you wish to retrieve batted ball data. Format: YYYY.
        min_bbe: Minimum batted ball events. "q" = qualified, or specify a number.
    
    Returns DataFrame with exit velo, barrel%, hard hit%, etc.
    """

    return pybaseball.statcast_batter_exitvelo_barrels(year, minBBE=min_bbe)


def get_hitter_by_name(year: int, first_name: str, last_name: str, min_pa: str = "0") -> dict:
    """
    Get expected stats for a hitter by name.
    
    ARGUMENTS
        year: The year to retrieve stats for
        first_name: Player's first name
        last_name: Player's last name
        min_pa: Minimum plate appearances to use when searching expected stats.
                 "0" returns all hitters, "q" returns qualified hitters.
    
    Returns dict with aggregated stats for that player.
    """
    df = get_hitter_expected_stats(year, min_pa=min_pa)
    
    # The name column is formatted as "last_name, first_name"
    name_col = 'last_name, first_name'
    
    # Try to find the player (case-insensitive)
    search_name = f"{last_name}, {first_name}"
    matches = df[df[name_col].str.lower() == search_name.lower()]
    
    if matches.empty:
        # Try partial match as fallback
        matches = df[
            (df[name_col].str.lower().str.contains(last_name.lower(), na=False))
        ]
    
    if matches.empty:
        return {}
    
    return matches.iloc[0].to_dict()


if __name__ == "__main__":
    import json
    
    year = 2026

    hitters = get_hitter_expected_stats(year, min_pa='q') ##qualified
    
    ##grab all mike trout stats
    mike_trout_stats = get_hitter_by_name(year, "Mike", "Trout", min_pa='q')
    print("Mike Trout's Expected Stats:")
    print(json.dumps(mike_trout_stats, indent=4))
