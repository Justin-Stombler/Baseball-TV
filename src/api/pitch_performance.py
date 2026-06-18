
import pandas as pd
import pybaseball
from typing import Union

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

def fetch_statcast_pitcher_pitch_arsenal(year: int, minP: int = 250, arsenal_type: str = "avg_speed") -> pd.DataFrame:
    """Retrieves high level stats on each pitcher's arsenal in a given year."""

    return pybaseball.statcast_pitcher_pitch_arsenal(year, minP=minP, arsenal_type=arsenal_type)

def fetch_statcast_pitcher_arsenal_stats(year: int, minPA: int = 25) -> pd.DataFrame:
    """Retrieves detailed stats on each pitcher's arsenal in a given year."""

    return pybaseball.statcast_pitcher_arsenal_stats(year, minPA=minPA)


def fetch_statcast_batter_pitch_arsenal(year: int, minPA: int = 25) -> pd.DataFrame:
    """Retrieves outcome data for batters split by pitch type in a given year."""

    return pybaseball.statcast_batter_pitch_arsenal(year, minPA=minPA)


def fetch_statcast_pitcher_expected_stats(year: int, minPA: Union[int, str] = 1) -> pd.DataFrame:
    """Retrieves season-level pitcher expected stats from Savant."""

    return pybaseball.statcast_pitcher_expected_stats(year, minPA=minPA)


def fetch_statcast_pitcher_exitvelo_barrels(year: int, minBBE: Union[int, str] = 1) -> pd.DataFrame:
    """Retrieves season-level pitcher batted-ball quality metrics from Savant."""

    return pybaseball.statcast_pitcher_exitvelo_barrels(year, minBBE=minBBE)

if __name__ == "__main__":
    # Example usage:
    pitcher_arsenal = fetch_statcast_pitcher_pitch_arsenal(2026)
    pitcher_arsenal_stats = fetch_statcast_pitcher_arsenal_stats(2026)
    print(pitcher_arsenal.head())
    print(pitcher_arsenal_stats.head())