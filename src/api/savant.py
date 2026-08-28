import pandas as pd
import pybaseball

from .player_stats import fetch_hitter_stats, fetch_pitcher_stats
from ..stats.pitcher_role import pitcher_position

##both needed to backport bat tracking data since that's not in this version of pybaseball
import requests
import io
from pybaseball.utils import sanitize_statcast_columns



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
    """Build a pitcher metadata map with team and position (SP/RP/TWP) keyed by player_id."""
    splits = fetch_pitcher_stats(season=season, player_pool=player_pool)
    rows = [
        {
            "player_id": p["player"]["id"],
            "team": p["team"]["name"],
            "position": pitcher_position(p),
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

def _statcast_batter_bat_tracking(year: int, minSwings: str = "q") -> pd.DataFrame:
    """Backport of pybaseball.statcast_batter_bat_tracking (not yet on the
    PyPI release we're pinned to). Mirrors pybaseball's own implementation
    so this can be dropped once the package catches up.
    """
    url = (
        "https://baseballsavant.mlb.com/leaderboard/bat-tracking/swing-path-attack-angle"
        f"?dateStart={year}-01-01&dateEnd={year}-12-31&gameType=Regular"
        f"&minSwings={minSwings}&minGroupSwings=1"
        f"&seasonStart={year}&seasonEnd={year}&type=batter&csv=true"
    )
    res = requests.get(url, timeout=None).content
    data = pd.read_csv(io.StringIO(res.decode("utf-8")))
    return sanitize_statcast_columns(data)


def fetch_statcast_batter_bat_tracking(year: int, min_swings: str = "q") -> pd.DataFrame:
    """Currently interested in bat speed, want to use that in the statcast player stats
    render for batters instead of xwOBA, since like who tf knows what that means other than the percentiles
    Ok I know what it is but come on this is more interesting I feel as a measure
    to go along with the exit velo and barrel% stuff.
    
    Uses above backport."""

    return _statcast_batter_bat_tracking(year, minSwings=min_swings)

if __name__ == "__main__":
    year = 2026

    hitter_expected = fetch_hitter_expected_stats(year, min_pa="q")
    pitcher_expected = fetch_pitcher_expected_stats(year, min_pa="q")
    batter_exitvelo = fetch_batter_exitvelo_barrels(year, min_bbe="q")
    pitcher_exitvelo = fetch_pitcher_exitvelo_barrels(year, min_bbe="q")
    hitter_bat_tracking = fetch_statcast_batter_bat_tracking(year, min_swings="q")
    print(f"Fetched {len(hitter_expected)} hitter expected stat rows")
    print(f"Fetched {len(pitcher_expected)} pitcher expected stat rows")
    print(f"Fetched {len(batter_exitvelo)} batter exit velo rows")
    print(f"Fetched {len(pitcher_exitvelo)} pitcher exit velo rows")
    print(f"Fetched {len(hitter_bat_tracking)} hitter bat tracking rows")

    ##show a full hitter 
    print(hitter_expected.head())
    print(pitcher_expected.head())
    print(batter_exitvelo.head())
    print(pitcher_exitvelo.head())
    print(hitter_bat_tracking.head())

    ##show all columns
    print(hitter_expected.columns)
    print(pitcher_expected.columns)
    print(batter_exitvelo.columns)
    print(pitcher_exitvelo.columns)
    print(hitter_bat_tracking.columns)