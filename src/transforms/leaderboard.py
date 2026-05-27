###1. Transform player data into aggregated top 10 lists by the whatever statistics desired
###2. Will require AL/NL split (it's in api.players)
###3. Leave option to filter for only qualfied players

from ..api.players import fetch_hitter_stats, fetch_pitcher_stats
from data.team_abbreviations import get_team_abbreviation
import json

relevant_stats = ['runs', 'doubles', 'triples', 'homeRuns', 'avg', 'ops']

def hitter_leaderboards(season: int = 2026, league: str = "AL", stat: str = "avg", qualified_only: bool = True) -> list[dict]:
    """Get top 5 hitters for a given stat and league."""
    player_pool = 'QUALIFIED' if qualified_only else 'ALL'
    splits = fetch_hitter_stats(season, player_pool=player_pool)

    league_players = [p for p in splits if p['league']['name'] == league]

    top_5 = sorted(league_players, key=lambda x: x['stat'].get(stat, 0), reverse=True)[:5]

    # Shape the output
    leaderboard = [
        {
            'name': p['player']['fullName'],
            'team': get_team_abbreviation(p['team']['name']),
            stat: p['stat'].get(stat),
        }
        for p in top_5
    ]

    return leaderboard

if __name__ == "__main__":
    top_averages = hitter_leaderboards(league = 'AL', stat = 'avg')
    print(top_averages)