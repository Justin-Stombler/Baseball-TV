###on its face this is meant to be very similar to the player_stats transform
###it will use same UI and stats as player_stats, so output needs to be in same format
###the question here is which stats?

from ..api.advanced_stats import fetch_advanced_hitting, fetch_advanced_pitching
from ..api.pitch_data import fetch_statcast_batter_pitches, fetch_statcast_pitcher_pitches
from .statcast_expected import expected_stats_list
from ..stats.percentiles import add_percentiles
from ..stats.qualification import filter_qualified
from ..stats.pitcher_role import build_role_lookup
from data.roster import is_rostered, get_team, get_jersey_number
import numpy as np


def spray_rates(player_id: int, is_pitcher: bool = False, season: int = 2026) -> dict:
    """Fetch per-pitch Statcast data for a single player and return pull/straight/oppo rates
    on balls in play. Only meant to be called for the one player currently being rendered
    (mirrors the per-player movement fetch used in pitch_arsenal)."""
    empty = {'pull_rate': None, 'straight_rate': None, 'oppo_rate': None}

    fetch = fetch_statcast_pitcher_pitches if is_pitcher else fetch_statcast_batter_pitches
    df = fetch(start_dt=f"{season}-03-01", end_dt=f"{season}-11-30", player_id=player_id)
    if df is None or df.empty or 'hc_x' not in df.columns or 'hc_y' not in df.columns:
        return empty

    bip = df.dropna(subset=['hc_x', 'hc_y'])
    if bip.empty:
        return empty

    ##Spray angle off home plate using the standard MLB Gameday coordinate origin (125.42, 198.27).
    ##Negative = pull side, positive = oppo side, flipped for lefties so it's always relative to the batter.
    angle = np.degrees(np.arctan2(bip['hc_x'] - 125.42, 198.27 - bip['hc_y']))
    angle = np.where(bip.get('stand') == 'L', -angle, angle)

    total = len(angle)
    if total == 0:
        return empty

    return {
        'pull_rate': (angle <= -15).sum() / total,
        'straight_rate': ((angle > -15) & (angle < 15)).sum() / total,
        'oppo_rate': (angle >= 15).sum() / total,
    }


def attach_spray_rates(player: dict, is_pitcher: bool = False, season: int = 2026) -> dict:
    """Merge pull/straight/oppo rates into a single player's stats dict in place, returning it."""
    player['stats'].update(spray_rates(player['id'], is_pitcher=is_pitcher, season=season))
    return player


def hitter_bb_profile(season: int = 2026, qualified_only: bool = True) -> list[dict]:
    """Transform hitter stats into a more usable format for stats rendering."""
    splits = fetch_advanced_hitting(season, player_pool='ALL')
    ##Only players on a current 40-man roster should ever reach the "all players" carousel/profile
    ##renders (leaderboards use qualified_only separately and are unaffected).
    splits = [p for p in splits if is_rostered(p['player']['id'])]
    if qualified_only:
        splits = filter_qualified(splits, 'HITTER', season)
    players = []
    
    for p in splits:
        stat = p['stat']
        players.append({
            'id': p['player']['id'],
            'name': p['player']['fullName'],
            'number': get_jersey_number(p['player']['fullName'], p['player']['id']),
            'team': get_team(p['player']['id']),
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
    ##Only players on a current 40-man roster should ever reach the "all players" carousel/profile
    ##renders (leaderboards use qualified_only separately and are unaffected).
    splits = [p for p in splits if is_rostered(p['player']['id'])]
    if qualified_only:
        splits = filter_qualified(splits, 'PITCHER', season)
    role_lookup = build_role_lookup(season)
    players = []
    
    for p in splits:
        stat = p['stat']
        players.append({
            'id': p['player']['id'],
            'name': p['player']['fullName'],
            'number': get_jersey_number(p['player']['fullName'], p['player']['id']),
            'team': get_team(p['player']['id']),
            'position': role_lookup.get(p['player']['id'], 'RP'),
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
    players = [p for p in players if p['position'] in ('SP', 'RP')]
    print(players[:5])  # Print top player