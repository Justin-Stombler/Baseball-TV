##This pulls all available stats from the MLB Stats API.
##Broken out into pitcher and hitter.

import statsapi

def fetch_hitter_stats(season: int = 2026) -> list:
    """Fetch all hitter stats with pagination."""
    all_splits = []
    offset = 0
    limit = 500
    
    while True:
        data = statsapi.get('stats', {
            'stats': 'season',
            'group': 'hitting',
            'season': season,
            'gameType': 'R',
            'playerPool': 'ALL',
            'limit': limit,
            'offset': offset,
        })
        
        splits = data['stats'][0]['splits']
        if not splits:
            break
            
        all_splits.extend(splits)
        
        if len(splits) < limit:
            break
            
        offset += limit
    
    return all_splits


def fetch_pitcher_stats(season: int = 2026) -> list:
    """Fetch all pitcher stats with pagination."""
    all_splits = []
    offset = 0
    limit = 500
    
    while True:
        data = statsapi.get('stats', {
            'stats': 'season',
            'group': 'pitching',
            'season': season,
            'gameType': 'R',
            'playerPool': 'ALL',
            'limit': limit,
            'offset': offset,
        })
        
        splits = data['stats'][0]['splits']
        if not splits:
            break
            
        all_splits.extend(splits)
        
        if len(splits) < limit:
            break
            
        offset += limit
    
    return all_splits

if __name__ == "__main__":
    hitters = fetch_hitter_stats()
    pitchers = fetch_pitcher_stats()
    
    print(f"Fetched {len(hitters)} hitter stats")
    print(f"Fetched {len(pitchers)} pitcher stats")