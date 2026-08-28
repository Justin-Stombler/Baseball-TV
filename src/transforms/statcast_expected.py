from ..api.savant import (
    fetch_hitter_expected_stats,
    fetch_pitcher_expected_stats,
    fetch_batter_exitvelo_barrels,
    fetch_pitcher_exitvelo_barrels,
    fetch_hitter_team_map,
    fetch_pitcher_team_map,
    fetch_statcast_batter_bat_tracking
)
from ..api.player_stats import fetch_hitter_stats, fetch_pitcher_stats
from ..api.advanced_stats import fetch_advanced_hitting, fetch_advanced_pitching
from ..api.pitch_data import fetch_statcast_pitcher_pitch_arsenal
from ..constants import DATA_DIR
from ..stats.percentiles import add_percentiles
from ..stats.qualification import qualification_threshold
import json
import unicodedata
import pandas as pd


with open(DATA_DIR / "roster.json") as f:
    roster_list = json.load(f)

def _normalize_name(name: str) -> str:
    if not name:
        return ""
    normalized = unicodedata.normalize("NFKD", name)
    ascii_name = normalized.encode("ascii", "ignore").decode("ascii")
    return " ".join(ascii_name.lower().strip().split())


rosters_by_id = {
    player['id']: player
    for player in roster_list
    if player.get('id') is not None
}

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
    """Get jersey number from roster.json, by id first then normalized name. Returns None if not listed."""
    if player_id in rosters_by_id:
        return rosters_by_id[player_id].get('number')
    return rosters_by_name.get(_normalize_name(display_name), {}).get("number")


def hitter_expected_transform(season: int = 2026, qualified_only: bool = True) -> list[dict]:
    """Transform hitter expected stats into a more usable format for stats rendering."""
    min_pa = str(round(qualification_threshold('HITTER', season))) if qualified_only else "0"
    hitter_df = fetch_hitter_expected_stats(season, min_pa=min_pa)
    ##BBE (batted ball events) excludes walks/Ks/HBP so it's always <= PA for the same player.
    ##Reusing min_pa as min_bbe over-filters this pull and drops qualified hitters from the join (NaN exit velo/barrel data).
    ##Qualification is already enforced by min_pa above, so pull this pool wide open to stay joinable.
    exit_df = fetch_batter_exitvelo_barrels(season, min_bbe="0")
    team_df = fetch_hitter_team_map(season=season, player_pool='ALL')
    hitter_stats = fetch_hitter_stats(season=season, player_pool='ALL')
    hitter_bat_tracking = fetch_statcast_batter_bat_tracking(season, min_swings="0")

    hitter_bat_tracking.rename(columns={'id': 'player_id'}, inplace=True)

    babip_map = {
        p["player"]["id"]: p["stat"].get("babip")
        for p in hitter_stats
        if p["stat"].get("babip") is not None
    }

    advanced_splits = fetch_advanced_hitting(season, player_pool='ALL')
    whiff_map = {}
    for p in advanced_splits:
        s = p['stat']
        swings = s.get('totalSwings') or 0
        misses = s.get('swingAndMisses') or 0
        whiff_map[p['player']['id']] = round(misses / swings * 100, 1) if swings > 0 else None

    ## merge on player_id so each hitter row gets exit velo/barrel data and roster metadata
    merged = hitter_df.merge(exit_df[['player_id', 'avg_hit_speed', 'brl_percent', 'avg_hit_angle', 'barrels', 'avg_distance']], on='player_id', how='left')
    merged = merged.merge(team_df[['player_id', 'team', 'position']], on='player_id', how='inner')
    merged = merged.merge(hitter_bat_tracking[['player_id', 'avg_bat_speed']], on='player_id', how='left')
    ##Only players on a current 40-man roster should ever reach the "all players" carousel/profile
    ##renders (leaderboards use qualified_only separately and are unaffected).
    merged = merged[merged['player_id'].isin(rosters_by_id.keys())]
    ##A pitcher with a rare pinch-hit PA can otherwise leak into this hitter pool with
    ##position='P', which would trip is_pitcher() checks downstream despite having no
    ##pitch-arsenal data of their own. TWP (true two-way players) are kept.
    merged = merged[~merged['position'].isin(['P', 'SP', 'RP'])]
    merged['babip'] = merged['player_id'].map(babip_map)
    players = []

    for _, row in merged.iterrows():
        pid = row.get('player_id')
        display_name = _display_name(row.get('last_name, first_name'))
        players.append({
            'id': pid,
            'name': display_name,
            'number': _roster_number_for_name(display_name, pid),
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
                'avg_bat_speed':  row.get('avg_bat_speed'),
                'whiff_percent':  whiff_map.get(pid),
            }
        })

    return players


def pitcher_expected_transform(season: int = 2026, qualified_only: bool = True) -> list[dict]:
    """Transform pitcher expected stats into a more usable format for stats rendering."""
    min_pa = str(round(qualification_threshold('PITCHER', season))) if qualified_only else "0"
    pitcher_df = fetch_pitcher_expected_stats(season, min_pa=min_pa)
    ##Same BBE-vs-PA mismatch as hitters: pull the exit velo/barrel pool wide open since qualification
    ##is already enforced by min_pa above.
    pitcher_exit_df = fetch_pitcher_exitvelo_barrels(season, min_bbe="0")
    team_df = fetch_pitcher_team_map(season=season, player_pool='ALL')

    ##I fundamentally disagree with a BABIP reconstruction for picthers for a few reasons
    ##but good lord do i dislike the ERA adjustment so here we are
    ##so....let's do it?

    ##BABIP = (H - HR) / (AB - K - BB + SF)
    pitcher_stats = fetch_pitcher_stats(season=season, player_pool='ALL')
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

    advanced_splits = fetch_advanced_pitching(season, player_pool='ALL')
    whiff_map = {}
    for p in advanced_splits:
        s = p['stat']
        swings = s.get('totalSwings') or 0
        misses = s.get('swingAndMisses') or 0
        whiff_map[p['player']['id']] = round(misses / swings * 100, 1) if swings > 0 else None

    ##Fastball velo = usage-weighted avg speed across the fastball family (4-seam, sinker/2-seam,
    ##cutter) so a pitcher who mixes FF/SI isn't just scored on whichever one pybaseball lists first.
    ##n_ff/n_si/n_fc are usage percentages (not raw counts), which is fine here since we only need
    ##relative weighting, not the true pitch total.
    speed_df = fetch_statcast_pitcher_pitch_arsenal(season, minP=1, arsenal_type="avg_speed")
    usage_df = fetch_statcast_pitcher_pitch_arsenal(season, minP=1, arsenal_type="n_")
    fastball_velo_map = {}
    if speed_df is not None and not speed_df.empty and usage_df is not None and not usage_df.empty:
        arsenal_df = speed_df.merge(usage_df, on='pitcher', how='inner')
        fb_pitch_cols = [('ff_avg_speed', 'n_ff'), ('si_avg_speed', 'n_si'), ('fc_avg_speed', 'n_fc')]
        for _, row in arsenal_df.iterrows():
            weighted_sum = 0.0
            total_weight = 0.0
            for speed_col, usage_col in fb_pitch_cols:
                speed = row.get(speed_col)
                usage = row.get(usage_col)
                if pd.notna(speed) and pd.notna(usage) and usage > 0:
                    weighted_sum += speed * usage
                    total_weight += usage
            if total_weight > 0:
                fastball_velo_map[int(row['pitcher'])] = round(weighted_sum / total_weight, 1)

    merged = pitcher_df.merge(
        pitcher_exit_df[['player_id', 'avg_hit_speed', 'brl_percent', 'avg_hit_angle', 'barrels', 'avg_distance']],
        on='player_id',
        how='left',
    )
    merged = merged.merge(team_df[['player_id', 'team', 'position']], on='player_id', how='inner')
    ##Only players on a current 40-man roster should ever reach the "all players" carousel/profile
    ##renders (leaderboards use qualified_only separately and are unaffected).
    merged = merged[merged['player_id'].isin(rosters_by_id.keys())]
    ##Savant's own min_pa filter on fetch_pitcher_expected_stats doesn't reliably exclude position
    ##players with a handful of mop-up pitching appearances (e.g. batters_faced=9), which would
    ##otherwise leak into this pitcher pool and clobber their hitter entry in expected_stats_list().
    merged = merged[merged['position'].isin(['SP', 'RP', 'TWP'])]
    merged['babip_against'] = merged['player_id'].map(babip_against_map)
    players = []

    for _, row in merged.iterrows():
        pid = row.get('player_id')
        display_name = _display_name(row.get('last_name, first_name'))
        players.append({
            'id': pid,
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
                'whiff_percent_against': whiff_map.get(pid),
                'fastball_velo': fastball_velo_map.get(pid),
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