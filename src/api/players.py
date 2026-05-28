##This pulls all available player stats from the MLB Stats API.
##By hitter and pitcher


import statsapi

def fetch_hitter_stats(season: int = 2026, player_pool: str = 'ALL') -> list:
    """Fetch all hitter stats with pagination."""
    all_splits = []
    offset = 0
    limit = 500
    
    while True:
        data = statsapi.get('stats', {
            'stats': 'season',
            'group': 'hitting',
            'season': season,
            'gameType': 'R', ##regular season
            'playerPool': player_pool,
            'limit': limit,
            'offset': offset,
        })
        
        splits = data['stats'][0]['splits']
        if not splits:
            break
            
        all_splits.extend(splits)

        ##detects last page
        if len(splits) < limit:
            break
            
        offset += limit
    
    return all_splits


def fetch_pitcher_stats(season: int = 2026, player_pool: str = 'ALL') -> list:
    """Fetch all pitcher stats with pagination."""
    all_splits = []
    offset = 0
    limit = 500
    
    while True:
        data = statsapi.get('stats', {
            'stats': 'season',
            'group': 'pitching',
            'season': season,
            'gameType': 'R', ##regular season
            'playerPool': player_pool,
            'limit': limit,
            'offset': offset,
        })
        
        splits = data['stats'][0]['splits']
        if not splits:
            break
        
        ##alias strikeOuts -> pitchingStrikeOuts to avoid conflict with hitting strikeOuts
        for split in splits:
            if 'strikeOuts' in split['stat']:
                split['stat']['pitchingStrikeOuts'] = split['stat'].pop('strikeOuts')
            
        all_splits.extend(splits)
        
        if len(splits) < limit:
            break
            
        offset += limit
    
    return all_splits

if __name__ == "__main__":
    hitters = fetch_hitter_stats(player_pool='ALL')
    pitchers = fetch_pitcher_stats(player_pool='ALL')
    
    print(f"Fetched {len(hitters)} hitter stats")
    print(f"Fetched {len(pitchers)} pitcher stats")