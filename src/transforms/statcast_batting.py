from ..api.statcast_batting import (
    fetch_hitter_expected_stats,
    fetch_pitcher_expected_stats,
    fetch_batter_exitvelo_barrels,
    fetch_pitcher_exitvelo_barrels,
    fetch_hitter_team_map,
    fetch_pitcher_team_map,
)
from ..api.player_stats import fetch_hitter_stats, fetch_pitcher_stats
from ..constants import DATA_DIR
from ..stats.percentiles import add_percentiles
import json
import unicodedata
import statsapi


with open(DATA_DIR / "roster.json") as f:
    roster_list = json.load(f)

_number_by_player_id = {}

def _normalize_name(name: str) -> str:
    if not name:
        return ""
    normalized = unicodedata.normalize("NFKD", name)
    ascii_name = normalized.encode("ascii", "ignore").decode("ascii")
    return " ".join(ascii_name.lower().strip().split())


rosters_by_name = {
    _normalize_name(player.get("name", "")): player
    for player in roster_list
    if player.get("name")
}


def _display_name(raw_name: str) -> str:
    if not raw_name:
        return ""
    if "," not in raw_name:
        return raw_name.strip()
    last, first = [part.strip() for part in raw_name.split(",", 1)]
    return f"{first} {last}".strip()


def _roster_number_for_name(display_name: str, player_id: int = None):
    """Get jersey number from roster first, then fallback to MLB person endpoint."""
    player = rosters_by_name.get(_normalize_name(display_name), {})
    number = player.get("number")
    if number:
        return number
    
    if player_id is None:
        return None
    
    if player_id in _number_by_player_id:
        return _number_by_player_id[player_id]
    
    try:
        person_data = statsapi.get('person', {'personId': player_id})
        number = person_data.get('people', [{}])[0].get('primaryNumber')
    except Exception:
        number = None
    
    _number_by_player_id[player_id] = number
    return number


def hitter_expected_transform(season: int = 2026, qualified_only: bool = True) -> list[dict]:
    """Transform hitter expected stats into a more usable format for stats rendering."""
    min_pa = "q" if qualified_only else "0"
    hitter_df = fetch_hitter_expected_stats(season, min_pa=min_pa)
    exit_df = fetch_batter_exitvelo_barrels(season, min_bbe=min_pa)
    team_df = fetch_hitter_team_map(season=season, player_pool='QUALIFIED' if qualified_only else 'ALL')
    hitter_stats = fetch_hitter_stats(season=season, player_pool='QUALIFIED' if qualified_only else 'ALL')
    babip_map = {
        p["player"]["id"]: p["stat"].get("babip")
        for p in hitter_stats
        if p["stat"].get("babip") is not None
    }

    ## merge on player_id so each hitter row gets exit velo/barrel data and roster metadata
    merged = hitter_df.merge(exit_df[['player_id', 'avg_hit_speed', 'brl_percent', 'avg_hit_angle', 'barrels', 'avg_distance']], on='player_id', how='left')
    merged = merged.merge(team_df[['player_id', 'team', 'position']], on='player_id', how='inner')
    merged['babip'] = merged['player_id'].map(babip_map)
    players = []

    for _, row in merged.iterrows():
        display_name = _display_name(row.get('last_name, first_name'))
        players.append({
            'id': row.get('player_id'),
            'name': display_name,
            'number': _roster_number_for_name(display_name, row.get('player_id')),
            'team': row.get('team'),
            'position': row.get('position'),
            'stats': {
                'pa':             row.get('pa'),
                'ba':             row.get('ba'),
                'xba':            row.get('est_ba'),
                'slg':            row.get('slg'),
                'xslg':           row.get('est_slg'),
                'slg_diff':       row.get('est_slg') - row.get('slg'),
                'woba':           row.get('woba'),
                'xwoba':          row.get('est_woba'),
                'exit_velocity':  row.get('avg_hit_speed'),
                'barrel_rate':    row.get('brl_percent'),
                'avg_hit_angle':  row.get('avg_hit_angle'),
                'barrels':        row.get('barrels'),
                'avg_distance':   row.get('avg_distance'),
                'babip':          row.get('babip'),
            }
        })

    return players


def pitcher_expected_transform(season: int = 2026, qualified_only: bool = True) -> list[dict]:
    """Transform pitcher expected stats into a more usable format for stats rendering."""
    min_pa = "q" if qualified_only else "0"
    pitcher_df = fetch_pitcher_expected_stats(season, min_pa=min_pa)
    pitcher_exit_df = fetch_pitcher_exitvelo_barrels(season, min_bbe=min_pa)
    team_df = fetch_pitcher_team_map(season=season, player_pool='QUALIFIED' if qualified_only else 'ALL')

    ##I fundamentally disagree with a BABIP reconstruction for picthers for a few reasons
    ##but good lord do i dislike the ERA adjustment so here we are
    ##so....let's do it?

    ##BABIP = (H - HR) / (AB - K - BB + SF)
    pitcher_stats = fetch_pitcher_stats(season=season, player_pool='QUALIFIED' if qualified_only else 'ALL')
    babip_against_map = {}
    for p in pitcher_stats:
        s = p["stat"]
        h = s.get('hits', 0)
        hr = s.get('homeRuns', 0)
        ab = s.get('atBats', 0)
        k = s.get('pitchingStrikeOuts', 0)
        bb = s.get('baseOnBalls', 0)
        sf = s.get('sacFlies', 0)
        denom = ab - k - bb + sf
        babip_against_map[p["player"]["id"]] = round((h - hr) / denom, 3) if denom > 0 else None

    merged = pitcher_df.merge(
        pitcher_exit_df[['player_id', 'avg_hit_speed', 'brl_percent', 'avg_hit_angle', 'barrels', 'avg_distance']],
        on='player_id',
        how='left',
    )
    merged = merged.merge(team_df[['player_id', 'team', 'position']], on='player_id', how='inner')
    merged['babip_against'] = merged['player_id'].map(babip_against_map)
    players = []

    for _, row in merged.iterrows():
        display_name = _display_name(row.get('last_name, first_name'))
        players.append({
            'id': row.get('player_id'),
            'name': display_name,
            'number': _roster_number_for_name(display_name, row.get('player_id')),
            'team': row.get('team'),
            'position': row.get('position') or 'P',
            'stats': {
                'pa':       row.get('pa'),
                'ba':       row.get('ba'),
                'xba_against':      row.get('est_ba'),
                'woba_against':     row.get('woba'),
                'xwoba_against':    row.get('est_woba'),
                'era':      row.get('era'),
                'xera':     row.get('xera'),
                'era_diff': row.get('era_minus_xera_diff'),
                'exit_velocity_against': row.get('avg_hit_speed'),
                'barrel_rate_against': row.get('brl_percent'),
                'avg_hit_angle': row.get('avg_hit_angle'),
                'barrels': row.get('barrels'),
                'avg_distance': row.get('avg_distance'),
                'babip_against': row.get('babip_against'),
            }
        })

    return players


def expected_stats_list(season: int = 2026, qualified_only: bool = True) -> list[dict]:
    """Get a combined list of hitter and pitcher expected stats."""
    hitters = hitter_expected_transform(season, qualified_only)
    pitchers = pitcher_expected_transform(season, qualified_only)

    hitters_with_percentiles = add_percentiles(hitters)
    pitchers_with_percentiles = add_percentiles(pitchers)

    return hitters_with_percentiles + pitchers_with_percentiles



if __name__ == "__main__":
    players = expected_stats_list(season=2026, qualified_only=True)

    ## only pitchers
    pitchers = pitcher_expected_transform(season=2026, qualified_only=True)
    print(pitchers[:5])

    ##only hitters
    hitters = hitter_expected_transform(season=2026, qualified_only=True)
    print(hitters[:5])