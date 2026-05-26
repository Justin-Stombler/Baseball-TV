###1. Transform player data into aggregated top 10 lists by the whatever statistics desired
###2. Will require AL/NL split (it's in api.players)
###3. Leave option to filter for only qualfied players

from ..api.players import fetch_hitter_stats
from ..api.players import fetch_pitcher_stats
import json
import os

##loading roster for number lookup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
with open(os.path.join(BASE_DIR, "data", "roster.json")) as f:
    roster_list = json.load(f)

rosters = {p['name']: p for p in roster_list} 

def hitter_transform(season: int = 2026, qualified_only: bool = True) -> list[dict]:
    """Transform hitter stats into a more usable format for stats rendering."""
    player_pool = 'QUALIFIED' if qualified_only else 'ALL'
    splits = fetch_hitter_stats(season, player_pool=player_pool)
    players = []
    
    for p in splits:
        stat = p['stat']
        players.append({
            'id': p['player']['id'],
            'name': p['player']['fullName'],
            'number': rosters.get(p['player']['fullName'], {}).get('number'),
            'team': p['team']['name'],
            'position': p['position']['abbreviation'],
            'stats': {
                'AVG': stat.get('avg'),
                'OPS': stat.get('ops'),
                'HR': stat.get('homeRuns'),
            }
        })
    
    return players


def pitcher_transform(season: int = 2026, qualified_only: bool = True) -> list[dict]:
    """Transform pitcher stats into a more usable format for stats rendering."""
    player_pool = 'QUALIFIED' if qualified_only else 'ALL'
    splits = fetch_pitcher_stats(season, player_pool=player_pool)
    players = []
    
    for p in splits:
        stat = p['stat']
        players.append({
            'id': p['player']['id'],
            'name': p['player']['fullName'],
            'number': rosters.get(p['player']['fullName'], {}).get('number'),
            'team': p['team']['name'],
            'position': p['position']['abbreviation'],
            'stats': {
                'ERA': stat.get('era'),
                'WHIP': stat.get('whip'),
                'SO': stat.get('strikeOuts'),
            }
        })
    
    return players

def player_list (season: int = 2026, qualified_only: bool = True) -> list[dict]:
    """Get a combined list of hitters and pitchers."""
    hitters = hitter_transform(season, qualified_only)
    pitchers = pitcher_transform(season, qualified_only)

    return hitters + pitchers

if __name__ == "__main__":
    players = player_list(season=2026, qualified_only=True)
    print(players[:1])  # Print top player