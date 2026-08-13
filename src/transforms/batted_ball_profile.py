###on its face this is meant to be very similar to the player_stats transform
###it will use same UI and stats as player_stats, so output needs to be in same format
###the question here is which stats?

from ..api.advanced_stats import fetch_advanced_hitting, fetch_advanced_pitching
from ..constants import DATA_DIR
from .statcast_batting import expected_stats_list
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

def hitter_bb_profile(season: int = 2026, qualified_only: bool = True) -> list[dict]:
    """Transform hitter stats into a more usable format for stats rendering."""
    splits = fetch_advanced_hitting(season, player_pool='ALL')
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
                'totalSwings': stat.get('totalSwings'),
                'swingAndMisses': stat.get('swingAndMisses'),
                'ballsInPlay': stat.get('ballsInPlay'),
                'popOuts': stat.get('popOuts'),
                'flyOuts': stat.get('flyOuts'),
                'lineOuts': stat.get('lineOuts'),
                'groundOuts': stat.get('groundOuts'),
                'flyHits': stat.get('flyHits'),
                'popHits': stat.get('popHits'),
                'lineHits': stat.get('lineHits'),
                'groundHits': stat.get('groundHits'),
                ##i want average for all 4 types and also percentage of occurence
                'popAverage': stat.get('popHits') / (stat.get('popOuts') + stat.get('popHits')) if stat.get('popOuts') + stat.get('popHits') > 0 else None,
                'flyAverage': stat.get('flyHits') / (stat.get('flyOuts') + stat.get('flyHits')) if stat.get('flyOuts') + stat.get('flyHits') > 0 else None,
                'lineAverage': stat.get('lineHits') / (stat.get('lineOuts') + stat.get('lineHits')) if stat.get('lineOuts') + stat.get('lineHits') > 0 else None,
                'groundAverage': stat.get('groundHits') / (stat.get('groundOuts') + stat.get('groundHits')) if stat.get('groundOuts') + stat.get('groundHits') > 0 else None,
                ## so above is success but below is distibution
                'popRate': (stat.get('popOuts') + stat.get('popHits')) / stat.get('ballsInPlay') if stat.get('ballsInPlay') > 0 else None,
                'flyRate': (stat.get('flyOuts') + stat.get('flyHits')) / stat.get('ballsInPlay') if stat.get('ballsInPlay') > 0 else None,
                'lineRate': (stat.get('lineOuts') + stat.get('lineHits')) / stat.get('ballsInPlay') if stat.get('ballsInPlay') > 0 else None,
                'groundRate': (stat.get('groundOuts') + stat.get('groundHits')) / stat.get('ballsInPlay') if stat.get('ballsInPlay') > 0 else None,
            },
        })

    return players


def pitcher_bb_profile(season: int = 2026, qualified_only: bool = True) -> list[dict]:
    """Transform pitcher stats into a more usable format for stats rendering."""
    splits = fetch_advanced_pitching(season, player_pool='ALL')
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
                'totalSwings': stat.get('totalSwings'),
                'swingAndMisses': stat.get('swingAndMisses'),
                'ballsInPlay': stat.get('ballsInPlay'),
                'popOuts': stat.get('popOuts'),
                'lineOuts': stat.get('lineOuts'),
                'groundOuts': stat.get('groundOuts'),
                'flyHits': stat.get('flyHits'),
                'popHits': stat.get('popHits'),
                'lineHits': stat.get('lineHits'),
                'groundHits': stat.get('groundHits'),
                ##i want average for all 4 types and also percentage of occurence
                'popAverage': stat.get('popHits') / (stat.get('popOuts') + stat.get('popHits')) if stat.get('popOuts') + stat.get('popHits') > 0 else None,
                'flyAverage': stat.get('flyHits') / (stat.get('flyOuts') + stat.get('flyHits')) if stat.get('flyOuts') + stat.get('flyHits') > 0 else None,
                'lineAverage': stat.get('lineHits') / (stat.get('lineOuts') + stat.get('lineHits')) if stat.get('lineOuts') + stat.get('lineHits') > 0 else None,
                'groundAverage': stat.get('groundHits') / (stat.get('groundOuts') + stat.get('groundHits')) if stat.get('groundOuts') + stat.get('groundHits') > 0 else None,
                ## so above is success but below is distibution
                'popRate': (stat.get('popOuts') + stat.get('popHits')) / stat.get('ballsInPlay') if stat.get('ballsInPlay') > 0 else None,
                'flyRate': (stat.get('flyOuts') + stat.get('flyHits')) / stat.get('ballsInPlay') if stat.get('ballsInPlay') > 0 else None,
                'lineRate': (stat.get('lineOuts') + stat.get('lineHits')) / stat.get('ballsInPlay') if stat.get('ballsInPlay') > 0 else None,
                'groundRate': (stat.get('groundOuts') + stat.get('groundHits')) / stat.get('ballsInPlay') if stat.get('ballsInPlay') > 0 else None,

            },
        })
    
    return players

def player_list (season: int = 2026, qualified_only: bool = True) -> list[dict]:
    """Get a combined list of hitters and pitchers."""
    hitters = hitter_bb_profile(season, qualified_only)
    pitchers = pitcher_bb_profile(season, qualified_only)
    expected_players = expected_stats_list(season, qualified_only)
    expected_by_id = {p.get('id'): p.get('stats', {}) for p in expected_players}

    # hitters_with_percentiles = add_percentiles(hitters)
    # pitchers_with_percentiles = add_percentiles(pitchers)

    players = hitters + pitchers
    for player in players:
        expected_stats = expected_by_id.get(player.get('id'), {})
        player['stats'].update(expected_stats)

    return players

if __name__ == "__main__":
    players = player_list(season=2026, qualified_only=True)
    
    ##only pitchers
    players = [p for p in players if p['position'] == 'P']
    print(players[:5])  # Print top player