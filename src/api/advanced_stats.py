from pathlib import Path
import statsapi

def fetch_advanced_hitting(season: int = 2026, player_pool: str = 'ALL') -> list:
    """Fetch seasonAdvanced hitting stats for a player."""
    all_splits = []
    offset = 0
    limit = 500

    while True:
        data = statsapi.get('stats', {
            'stats': 'seasonAdvanced',
            'group': 'hitting',
            'season': season,
            'gameType': 'R',
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


def fetch_advanced_pitching(season: int = 2026) -> list:
    """Fetch seasonAdvanced pitching stats for a player."""

    all_splits = []
    offset = 0
    limit = 500

    while True:

        data = statsapi.get('stats', {
            'stats': 'seasonAdvanced',
            'group': 'pitching',
            'season': season,
            'gameType': 'R',
            'limit': limit,
            'offset': offset
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

if __name__ == "__main__":
    hitters = fetch_advanced_hitting()
    pitchers = fetch_advanced_pitching()

    print(f"Fetched {len(hitters)} advanced hitting splits")
    print(f"Fetched {len(pitchers)} advanced pitching splits")
    print("Example advanced hitting split:", hitters[0] if hitters else "No data")
    print("Example advanced pitching split:", pitchers[0] if pitchers else "No data")
