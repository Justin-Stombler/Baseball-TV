###1. Transform player data into aggregated top 10 lists by the whatever statistics desired
###2. Will require AL/NL split (it's in api.players)
###3. Leave option to filter for only qualfied players

from ..api.players import fetch_hitter_stats, fetch_pitcher_stats
from data.team_abbreviations import get_team_abbreviation
from ..stats.config import STAT_CONFIG

def generate_leaderboard(season: int = 2026, league: str = "AL", stat: str = "avg", qualified_only: bool = True) -> list[dict]:
    """Get top 5 players for a given stat, league, and player type."""
    player_pool = 'QUALIFIED' if qualified_only else 'ALL'

    type = STAT_CONFIG.get(stat, {}).get('type')

    if type == 'hitting':
        splits = fetch_hitter_stats(season, player_pool=player_pool)
    elif type == 'pitching':
        splits = fetch_pitcher_stats(season, player_pool=player_pool)
    else:
        raise ValueError("Type must be 'hitter' or 'pitcher'")

    league_players = [p for p in splits if p['league']['name'] == league]
    league_players = [p for p in league_players if p.get('stat', {}).get(stat) is not None]

    direction = STAT_CONFIG.get(stat, {}).get('ascending')
    top_5 = sorted(league_players, key=lambda x: x['stat'].get(stat, 0), reverse=not direction)[:5]

    ##pull sorting direction from stats config

    leaderboard = [
        {
            'league': p['league']['name'],
            'name': p['player']['fullName'],
            'team': get_team_abbreviation(p['team']['name']),
            'team_name': p['team']['name'],
            stat: p['stat'].get(stat),
        }
        for p in top_5
    ]

    return leaderboard

if __name__ == "__main__":
    import random
    league = random.choice(['AL', 'NL'])
    stat = 'pitchingStrikeOuts'
    top_averages = generate_leaderboard(league=league, stat=stat)
    print(top_averages)