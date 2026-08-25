###File purpose is twofold
###1. Transform raw data into specific points to display (see design doc)
###2. Leave option to filter for only qualfied players

from ..api.player_stats import fetch_hitter_stats, fetch_pitcher_stats
from ..stats.percentiles import add_percentiles
from ..stats.qualification import filter_qualified
from ..stats.pitcher_role import pitcher_position
from data.roster import is_rostered, get_team, get_jersey_number

def hitter_transform(season: int = 2026, qualified_only: bool = True) -> list[dict]:
    """Transform hitter stats into a more usable format for stats rendering."""
    splits = fetch_hitter_stats(season, player_pool='ALL')
    ##Only players on a current 40-man roster should ever reach the "all players" carousel/profile
    ##renders (leaderboards use qualified_only separately and are unaffected). This drops anyone
    ##released, DFA'd, or otherwise off every roster even if they still have season stats on file.
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
    ##Only players on a current 40-man roster should ever reach the "all players" carousel/profile
    ##renders (leaderboards use qualified_only separately and are unaffected).
    splits = [p for p in splits if is_rostered(p['player']['id'])]
    if qualified_only:
        splits = filter_qualified(splits, 'PITCHER', season)
    players = []
    
    for p in splits:
        stat = p['stat']
        players.append({
            'id': p['player']['id'],
            'name': p['player']['fullName'],
            'number': get_jersey_number(p['player']['fullName'], p['player']['id']),
            'team': get_team(p['player']['id']),
            'position': pitcher_position(p),
            'stats': {
                'inningsPitched': stat.get('inningsPitched'),
                'era': stat.get('era'),
                'whip': stat.get('whip'),
                'homeRunsPer9': stat.get('homeRunsPer9'),
                'pitchingStrikeOuts': stat.get('pitchingStrikeOuts'),
                'strikeoutsPer9Inn': stat.get('strikeoutsPer9Inn')
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
    players = [p for p in players if p['position'] in ('SP', 'RP')]
    print(players[:5])  # Print top player