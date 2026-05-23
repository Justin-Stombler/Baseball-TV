# mlb_data.py

import statsapi

def get_hitter_stats(season: int = 2026) -> list[dict]:
    data = statsapi.get('stats', {
        'stats': 'season',
        'group': 'hitting',
        'season': season,
        'gameType': 'R',
        'limit': 500,
    })
    
    players = []
    for p in data['stats'][0]['splits']:
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
    return players


def get_pitcher_stats(season: int = 2026) -> list[dict]:
    data = statsapi.get('stats', {
        'stats': 'season',
        'group': 'pitching',
        'season': season,
        'gameType': 'R',
        'limit': 500,
    })
    
    players = []
    for p in data['stats'][0]['splits']:
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
    return players

if __name__ == "__main__":
    hitters = get_hitter_stats()
    pitchers = get_pitcher_stats()
    print(hitters[:3])
    print(pitchers[:3])