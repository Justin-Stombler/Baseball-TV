###File purpose is twofold
###1. Transform raw data into specific points to display (see design doc)
###2. Leave option to filter for only qualfied players

from .api import fetch_hitter_stats
from .api import fetch_pitcher_stats
from .stats.percentiles import add_percentiles
import json
import os

##loading roster for number lookup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(BASE_DIR, "data", "roster.json")) as f:
    roster_list = json.load(f)

rosters = {p['name']: p for p in roster_list} 

def hitter_transform(season: int = 2026, qualified_only: bool = True) -> list[dict]:
    """Transform hitter stats into a more usable format."""
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
    """Transform pitcher stats into a more usable format."""
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

    hitters_with_percentiles = add_percentiles(hitters)
    pitchers_with_percentiles = add_percentiles(pitchers)

    return hitters_with_percentiles + pitchers_with_percentiles

if __name__ == "__main__":
    players = player_list(season=2026, qualified_only=True)
    print(players[:1])  # Print top player