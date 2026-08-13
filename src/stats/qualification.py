###Baseball Savant style qualification (2.1 PA/G hitters, 1.25 PA/G pitchers)
###Rates come from QUALIFICATION_CONFIG in config.py - don't redefine them here.
###Used only by the player cycle (player_stats -> bio_list -> statcast_batting -> batted_ball_profile)
###so relievers and part-time bench bats aren't excluded from random player selection
###the way statsapi's playerPool='QUALIFIED' excludes them.
###Leaderboards intentionally keep using statsapi's QUALIFIED pool (see config.py comment)
###to mirror the site's official leaderboards - don't use this there.

from ..api.team_performance import fetch_team_performance
from ..config import QUALIFICATION_CONFIG


def _team_games_played(season: int = 2026) -> int:
    """Games played by the team furthest into its season, standing in for the 'G' in PA/G."""
    rows = fetch_team_performance(season)
    games = [r.get('wins', 0) + r.get('losses', 0) for r in rows]
    return max(games) if games else 162


def qualification_threshold(role: str, season: int = 2026) -> float:
    """PA (role='HITTER') or batters-faced (role='PITCHER') threshold, per QUALIFICATION_CONFIG."""
    return QUALIFICATION_CONFIG[role] * _team_games_played(season)


def filter_qualified(splits: list[dict], role: str, season: int = 2026) -> list[dict]:
    """Keep only statsapi splits meeting the Savant-style threshold for role='HITTER'|'PITCHER'."""
    stat_key = 'plateAppearances' if role == 'HITTER' else 'battersFaced'
    threshold = qualification_threshold(role, season)
    result = []
    for s in splits:
        value = s.get('stat', {}).get(stat_key)
        try:
            if value is not None and float(value) >= threshold:
                result.append(s)
        except (TypeError, ValueError):
            continue
    return result
