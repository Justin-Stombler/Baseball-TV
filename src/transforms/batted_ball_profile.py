###on its face this is meant to be very similar to the player_stats transform
###it will use same UI and stats as player_stats, so output needs to be in same format
###the question here is which stats?

from ..api.advanced_stats import fetch_advanced_hitting, fetch_advanced_pitching
from ..constants import DATA_DIR
from ..stats.percentiles import add_percentiles
import json

##loading roster for number lookup
with open(DATA_DIR / "roster.json") as f:
    roster_list = json.load(f)

rosters = {p['name']: p for p in roster_list} 

def hitter_transform(season: int = 2026, qualified_only: bool = True) -> list[dict]:
    """Transform hitter stats into a more usable format for stats rendering."""
    player_pool = 'QUALIFIED' if qualified_only else 'ALL'
    splits = fetch_advanced_hitting(season, player_pool=player_pool)
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
                'avg': stat.get('avg'),
                'obp': stat.get('obp'),
                'ops': stat.get('ops'),
                'homeRuns': stat.get('homeRuns'),
                'rbi': stat.get('rbi')},
        })
    
    return players


def pitcher_transform(season: int = 2026, qualified_only: bool = True) -> list[dict]:
    """Transform pitcher stats into a more usable format for stats rendering."""
    player_pool = 'QUALIFIED' if qualified_only else 'ALL'
    splits = fetch_advanced_pitching(season, player_pool=player_pool)
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
                'inningsPitched': stat.get('inningsPitched'),
                'era': stat.get('era'),
                'whip': stat.get('whip'),
                'homeRunsPer9': stat.get('homeRunsPer9'),
                'pitchingStrikeOuts': stat.get('pitchingStrikeOuts'),
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
    
    ##only pitchers
    players = [p for p in players if p['position'] == 'P']
    print(players[:5])  # Print top player