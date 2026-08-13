###File purpose is twofold
###1. Transform raw data into specific points to display (see design doc)
###2. Leave option to filter for only qualfied players

from ..api.player_stats import fetch_hitter_stats, fetch_pitcher_stats
from ..constants import DATA_DIR
from ..stats.percentiles import add_percentiles
from ..stats.qualification import filter_qualified
import json
import statsapi

##loading roster for number lookup
with open(DATA_DIR / "roster.json") as f:
    roster_list = json.load(f)

rosters = {p['name']: p for p in roster_list}
_number_by_player_id = {}

def _lookup_jersey_number(full_name: str, player_id: int):
    """Get jersey number from roster first, then fallback to MLB person endpoint."""
    number = rosters.get(full_name, {}).get('number')
    if number:
        return number

    if player_id in _number_by_player_id:
        return _number_by_player_id[player_id]

    try:
        person_data = statsapi.get('person', {'personId': player_id})
        number = person_data.get('people', [{}])[0].get('primaryNumber')
    except Exception:
        number = None

    _number_by_player_id[player_id] = number
    return number 

def hitter_transform(season: int = 2026, qualified_only: bool = True) -> list[dict]:
    """Transform hitter stats into a more usable format for stats rendering."""
    splits = fetch_hitter_stats(season, player_pool='ALL')
    if qualified_only:
        splits = filter_qualified(splits, 'HITTER', season)
    players = []
    
    for p in splits:
        stat = p['stat']
        players.append({
            'id': p['player']['id'],
            'name': p['player']['fullName'],
            'number': _lookup_jersey_number(p['player']['fullName'], p['player']['id']),
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
    splits = fetch_pitcher_stats(season, player_pool='ALL')
    if qualified_only:
        splits = filter_qualified(splits, 'PITCHER', season)
    players = []
    
    for p in splits:
        stat = p['stat']
        players.append({
            'id': p['player']['id'],
            'name': p['player']['fullName'],
            'number': _lookup_jersey_number(p['player']['fullName'], p['player']['id']),
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