import pandas as pd
import pybaseball

from .player_stats import fetch_hitter_stats, fetch_pitcher_stats


def fetch_hitter_team_map(season: int = 2026, player_pool: str = "ALL") -> pd.DataFrame:
    """Build a hitter metadata map with team and position keyed by player_id."""
    splits = fetch_hitter_stats(season=season, player_pool=player_pool)
    rows = [
        {
            "player_id": p["player"]["id"],
            "team": p["team"]["name"],
            "position": p["position"]["abbreviation"],
        }
        for p in splits
    ]
    return pd.DataFrame(rows).drop_duplicates(subset=["player_id"])


def fetch_pitcher_team_map(season: int = 2026, player_pool: str = "ALL") -> pd.DataFrame:
    """Build a pitcher metadata map with team and position keyed by player_id."""
    splits = fetch_pitcher_stats(season=season, player_pool=player_pool)
    rows = [
        {
            "player_id": p["player"]["id"],
            "team": p["team"]["name"],
            "position": p["position"]["abbreviation"],
        }
        for p in splits
    ]
    return pd.DataFrame(rows).drop_duplicates(subset=["player_id"])

def fetch_hitter_expected_stats(year: int, min_pa: str = "q") -> pd.DataFrame:
    """Fetch expected stats for all hitters in a given year.
    
    ARGUMENTS
        year: The year to retrieve stats for. Format: YYYY.
        min_pa: Minimum plate appearances. "q" = qualified, or specify a number like "100".
    
    Returns DataFrame with columns like: xBA, xSLG, xwOBA, exit_velocity, etc.
    """
    return pybaseball.statcast_batter_expected_stats(year, minPA=min_pa)

def fetch_pitcher_expected_stats(year: int, min_pa: str = "q") -> pd.DataFrame:
    """Fetch expected stats for all pitchers in a given year.
    
    ARGUMENTS
        year: The year to retrieve stats for. Format: YYYY.
        min_pa: Minimum plate appearances faced. "q" = qualified, or specify a number.
    
    Returns DataFrame with columns like: xBA, xwOBA, xERA, etc.
    """
    return pybaseball.statcast_pitcher_expected_stats(year, minPA=min_pa)


def fetch_batter_exitvelo_barrels(year: int, min_bbe: str = "q") -> pd.DataFrame:
    """Fetch exit velo and barrel data for all batters in a given year.
    
    ARGUMENTS
        year: The year to retrieve stats for. Format: YYYY.
        min_bbe: Minimum batted ball events. "q" = qualified, or specify a number.
    
    Returns DataFrame with exit velo, barrel%, hard hit%, etc.
    """
    return pybaseball.statcast_batter_exitvelo_barrels(year, minBBE=min_bbe)

def fetch_pitcher_exitvelo_barrels(year: int, min_bbe: str = "q") -> pd.DataFrame:
    """Fetch exit velo and barrel data for all pitchers in a given year.
    
    ARGUMENTS
        year: The year to retrieve stats for. Format: YYYY.
        min_bbe: Minimum batted ball events allowed. "q" = qualified, or specify a number.
    
    Returns DataFrame with exit velo, barrel%, hard hit%, etc. allowed by each pitcher.
    """
    return pybaseball.statcast_pitcher_exitvelo_barrels(year, minBBE=min_bbe)


if __name__ == "__main__":
    year = 2026

    hitter_expected = fetch_hitter_expected_stats(year, min_pa="q")
    pitcher_expected = fetch_pitcher_expected_stats(year, min_pa="q")
    batter_exitvelo = fetch_batter_exitvelo_barrels(year, min_bbe="q")
    pitcher_exitvelo = fetch_pitcher_exitvelo_barrels(year, min_bbe="q")
    print(f"Fetched {len(hitter_expected)} hitter expected stat rows")
    print(f"Fetched {len(pitcher_expected)} pitcher expected stat rows")
    print(f"Fetched {len(batter_exitvelo)} batter exit velo rows")
    print(f"Fetched {len(pitcher_exitvelo)} pitcher exit velo rows")

    ##show a full hitter 
    print(hitter_expected.head())
    print(pitcher_expected.head())
    print(batter_exitvelo.head())
    print(pitcher_exitvelo.head())

    ##show all columns
    print(hitter_expected.columns)
    print(pitcher_expected.columns)
    print(batter_exitvelo.columns)
    print(pitcher_exitvelo.columns)