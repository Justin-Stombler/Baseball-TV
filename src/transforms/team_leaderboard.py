###1. Transform player data into aggregated top 10 lists by the whatever statistics desired
###2. Will require AL/NL split (it's in api.players)
###3. Leave option to filter for only qualfied players

from ..api.player_stats import fetch_hitter_stats, fetch_pitcher_stats
from data.team_abbreviations import get_team_abbreviation
from ..stats.config import STAT_CONFIG


def _is_pitcher(player: dict) -> bool:
    """Return True when a player record is a pitcher entry."""
    return player.get('position', {}).get('abbreviation') == 'P'


def _to_float_or_none(value) -> float | None:
    """Parse a stat value to float; return None when value is not numeric."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def get_available_teams(
    season: int = 2026,
    stat: str = "avg",
    qualified_only: bool = False,
) -> list[str]:
    """Return team names that have at least one player with this stat."""
    player_pool = 'QUALIFIED' if qualified_only else 'ALL'
    stat_type = STAT_CONFIG.get(stat, {}).get('type')

    if stat_type == 'hitting':
        splits = fetch_hitter_stats(season, player_pool=player_pool)
    elif stat_type == 'pitching':
        splits = fetch_pitcher_stats(season, player_pool=player_pool)
    else:
        raise ValueError("Type must be 'hitter' or 'pitcher'")

    teams = {
        p['team']['name']
        for p in splits
        if p.get('team', {}).get('name')
        and p.get('stat', {}).get(stat) is not None
        and _to_float_or_none(p.get('stat', {}).get(stat)) is not None
        and (stat_type != 'pitching' or _is_pitcher(p))
    }
    return sorted(teams)

def generate_team_leaderboard(team: str = 'Baltimore Orioles', season: int = 2026, stat: str = "avg", qualified_only: bool = False) -> list[dict]:
    """Get top 5 players for a given stat, league, and player type."""
    player_pool = 'QUALIFIED' if qualified_only else 'ALL'

    type = STAT_CONFIG.get(stat, {}).get('type')

    if type == 'hitting':
        splits = fetch_hitter_stats(season, player_pool=player_pool)
    elif type == 'pitching':
        splits = fetch_pitcher_stats(season, player_pool=player_pool)
    else:
        raise ValueError("Type must be 'hitter' or 'pitcher'")

    team_players = [p for p in splits if p['team']['name'] == team]
    team_players = [p for p in team_players if p.get('stat', {}).get(stat) is not None]
    if type == 'pitching':
        team_players = [p for p in team_players if _is_pitcher(p)]

    sortable_players = [
        p for p in team_players
        if _to_float_or_none(p.get('stat', {}).get(stat)) is not None
    ]

    direction = STAT_CONFIG.get(stat, {}).get('ascending')
    top_5 = sorted(
        sortable_players,
        key=lambda p: _to_float_or_none(p.get('stat', {}).get(stat)),
        reverse=not direction,
    )[:5]

    ##pull sorting direction from stats config

    leaderboard = [
        {
            'league': p['league']['name'],
            'name': p['player']['fullName'],
            'team': get_team_abbreviation(p['team']['name']),
            'team_name': p['team']['name'],
            'position': p['position']['abbreviation'],
            stat: p['stat'].get(stat),
        }
        for p in top_5
    ]

    while len(leaderboard) < 5:
        leaderboard.append(
            {
                'league': '',
                'name': 'N/A',
                'team': get_team_abbreviation(team),
                'team_name': team,
                'position': 'N/A',
                stat: 'N/A',
            }
        )

    return leaderboard

if __name__ == "__main__":
    stat = 'homeRuns'
    top_averages = generate_team_leaderboard(team='Baltimore Orioles', stat=stat)
    print(top_averages)