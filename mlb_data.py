# mlb_data.py

import statsapi

def get_hitter_stats(season: int = 2026) -> list[dict]:
    """Fetch all hitter stats with pagination."""
    players = []
    offset = 0
    limit = 500
    
    while True:
        data = statsapi.get('stats', {
            'stats': 'season',
            'group': 'hitting',
            'season': season,
            'gameType': 'R',
            'limit': limit,
            'offset': offset,
        })
        
        splits = data['stats'][0]['splits']
        if not splits:
            break
        
        for p in splits:
            stat = p['stat']
            players.append({
                'id': p['player']['id'],
                'name': p['player']['fullName'],
                'team': p['team']['name'],
                'stats': {
                    'AVG': stat.get('avg'),
                    'OPS': stat.get('ops'),
                    'HR': stat.get('homeRuns'),
                }
            })
        
        if len(splits) < limit:
            break
            
        offset += limit
    
    return players


def get_pitcher_stats(season: int = 2026) -> list[dict]:
    """Fetch all pitcher stats with pagination."""
    players = []
    offset = 0
    limit = 500
    
    while True:
        data = statsapi.get('stats', {
            'stats': 'season',
            'group': 'pitching',
            'season': season,
            'gameType': 'R',
            'limit': limit,
            'offset': offset,
        })
        
        splits = data['stats'][0]['splits']
        if not splits:
            break
        
        for p in splits:
            stat = p['stat']
            players.append({
                'id': p['player']['id'],
                'name': p['player']['fullName'],
                'team': p['team']['name'],
                'stats': {
                    'IP': stat.get('inningsPitched'),
                    'ERA': stat.get('era'),
                    'WHIP': stat.get('whip'),
                }
            })
        
        if len(splits) < limit:
            break
            
        offset += limit
    
    return players

if __name__ == "__main__":
    hitters = get_hitter_stats()
    pitchers = get_pitcher_stats()
    print(hitters[:3])
    print(pitchers[:3])