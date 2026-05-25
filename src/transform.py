###File purpose is twofold
###1. Transform raw data into specific points to display (see design doc)
###2. Leave option to filter for only qualfied players

from api import fetch_hitter_stats
from api import fetch_pitcher_stats

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
    hitters = hitter_transform(qualified_only=True)
    pitchers = pitcher_transform(qualified_only=True)