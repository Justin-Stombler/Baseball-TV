from ..api.pitch_performance import (
    fetch_statcast_pitcher_arsenal_stats,
    fetch_statcast_pitcher_exitvelo_barrels,
    fetch_statcast_pitcher_expected_stats,
    fetch_statcast_pitcher_pitch_arsenal,
    fetch_pitcher_team_map,
)
from ..api.advanced_stats import fetch_advanced_pitching
from ..api.player_stats import fetch_pitcher_stats
from ..stats.percentiles import add_percentiles
import pandas as pd
import json


def _display_name(raw_name: str) -> str:
    if not raw_name:
        return ""
    if "," not in raw_name:
        return raw_name.strip()
    last, first = [part.strip() for part in raw_name.split(",", 1)]
    return f"{first} {last}".strip()


def pitch_performance_pitcher(season: int = 2026, qualified_only: bool = True) -> list[dict]:
    """Transform pitcher pitch-by-pitch performance stats into a usable format.
    
    Returns list of pitchers with player_id, name, team, position, and a dict of pitches
    containing performance stats (BA, SLG, WOBA, etc.) plus pitcher-specific details (velocity, spin rate).
    All pitch types included (min_pa=1) so pitch_usage reflects full arsenal.
    """
    min_pa = 1

    # Fetch performance stats
    arsenal_stats_df = fetch_statcast_pitcher_arsenal_stats(season, minPA=min_pa)
    if arsenal_stats_df is None or arsenal_stats_df.empty:
        return []

    # Fetch velocity/spin details by pitch (minP=250 is pybaseball's safe minimum)
    try:
        pitch_details_df = fetch_statcast_pitcher_pitch_arsenal(season, minP=250, arsenal_type="avg_speed")
    except:
        pitch_details_df = None

    # Merge with team/position data
    team_df = fetch_pitcher_team_map(season=season, player_pool='QUALIFIED' if qualified_only else 'ALL')
    merged = arsenal_stats_df.merge(
        team_df[['player_id', 'team', 'position']],
        on='player_id',
        how='left'
    )

    if qualified_only:
        all_team_df = fetch_pitcher_team_map(season=season, player_pool='ALL')
        merged = merged.merge(
            all_team_df[['player_id', 'team', 'position']].rename(
                columns={'team': 'team_all', 'position': 'position_all'}
            ),
            on='player_id',
            how='left'
        )
        merged['team'] = merged['team'].fillna(merged['team_all'])
        merged['position'] = merged['position'].fillna(merged['position_all'])

    # Build pitch detail lookup if available
    pitch_detail_lookup = {}
    if pitch_details_df is not None and not pitch_details_df.empty:
        for _, row in pitch_details_df.iterrows():
            key = (row.get('IDfg'), row.get('Pitch'))  # pitcher ID + pitch type
            pitch_detail_lookup[key] = {
                'avg_speed': float(row.get('Velo')) if pd.notna(row.get('Velo')) else None,
                'spin_rate': float(row.get('Spin Rate')) if pd.notna(row.get('Spin Rate')) else None,
            }
    
    expected_lookup = {}
    expected_df = fetch_statcast_pitcher_expected_stats(season, minPA=1)
    for _, row in expected_df.iterrows():
        player_id = row.get('player_id')
        if pd.isna(player_id):
            continue
        expected_lookup[int(player_id)] = {
            'ba': float(row.get('ba')) if pd.notna(row.get('ba')) else None,
            'slg': float(row.get('slg')) if pd.notna(row.get('slg')) else None,
            'pa': int(row.get('pa')) if pd.notna(row.get('pa')) else None,
        }

    batted_ball_lookup = {}
    batted_ball_df = fetch_statcast_pitcher_exitvelo_barrels(season, minBBE=1)
    for _, row in batted_ball_df.iterrows():
        player_id = row.get('player_id')
        if pd.isna(player_id):
            continue
        batted_ball_lookup[int(player_id)] = {
            'hard_hit_percent': float(row.get('ev95percent')) if pd.notna(row.get('ev95percent')) else None,
            'hard_hits': int(row.get('ev95plus')) if pd.notna(row.get('ev95plus')) else None,
        }

    season_count_lookup = {}
    for split in fetch_pitcher_stats(season, player_pool='ALL'):
        player_id = split.get('player', {}).get('id')
        if player_id is None:
            continue
        stat = split.get('stat', {})
        season_count_lookup[int(player_id)] = {
            'hits': int(stat.get('hits')) if stat.get('hits') is not None else None,
        }

    advanced_lookup = {}
    for split in fetch_advanced_pitching(season, player_pool='ALL'):
        player_id = split.get('player', {}).get('id')
        if player_id is None:
            continue
        stat = split.get('stat', {})
        advanced_lookup[int(player_id)] = {
            'swings': int(stat.get('totalSwings')) if stat.get('totalSwings') is not None else None,
            'whiffs': int(stat.get('swingAndMisses')) if stat.get('swingAndMisses') is not None else None,
        }

    pitchers = []

    for pitcher_id, group in merged.groupby('player_id', dropna=True):
        first = group.iloc[0]
        display_name = _display_name(first.get('last_name, first_name', ''))
        team = first.get('team') if pd.notna(first.get('team')) else first.get('team_name_alt')
        position = first.get('position')

        # Keep this transform pitcher-only; exclude position players with occasional pitching appearances.
        if position not in ('SP', 'RP', 'TWP'):
            continue

        pitches = {}
        for _, row in group.iterrows():
            pitch_code = str(row.get('pitch_type', '')).strip()
            if pitch_code:
                # Build pitch entry with performance stats
                pitch_entry = {
                    "pitch_name": row.get('pitch_name'),
                    "run_value_per_100": float(row.get('run_value_per_100')) if pd.notna(row.get('run_value_per_100')) else None,
                    "run_value": float(row.get('run_value')) if pd.notna(row.get('run_value')) else None,
                    "pitches": int(row.get('pitches')) if pd.notna(row.get('pitches')) else None,
                    "pitch_usage": float(row.get('pitch_usage')) if pd.notna(row.get('pitch_usage')) else None,
                    "pa": int(row.get('pa')) if pd.notna(row.get('pa')) else None,
                    "ba": float(row.get('ba')) if pd.notna(row.get('ba')) else None,
                    "slg": float(row.get('slg')) if pd.notna(row.get('slg')) else None,
                    "woba": float(row.get('woba')) if pd.notna(row.get('woba')) else None,
                    "whiff_percent": float(row.get('whiff_percent')) if pd.notna(row.get('whiff_percent')) else None,
                    "k_percent": float(row.get('k_percent')) if pd.notna(row.get('k_percent')) else None,
                    "put_away": float(row.get('put_away')) if pd.notna(row.get('put_away')) else None,
                    "est_ba": float(row.get('est_ba')) if pd.notna(row.get('est_ba')) else None,
                    "est_slg": float(row.get('est_slg')) if pd.notna(row.get('est_slg')) else None,
                    "est_woba": float(row.get('est_woba')) if pd.notna(row.get('est_woba')) else None,
                    "hard_hit_percent": float(row.get('hard_hit_percent')) if pd.notna(row.get('hard_hit_percent')) else None,
                }
                
                # Add pitcher-specific velocity/spin data if available
                lookup_key = (pitcher_id, pitch_code)
                if lookup_key in pitch_detail_lookup:
                    pitch_entry.update(pitch_detail_lookup[lookup_key])
                
                pitches[pitch_code] = pitch_entry

        if not pitches:
            continue

        # Aggregate requested expected stats at pitcher level using PA-weighted means.
        weights = pd.to_numeric(group['pa'], errors='coerce').fillna(0)

        def _weighted(col: str):
            vals = pd.to_numeric(group[col], errors='coerce')
            valid = vals.notna() & (weights > 0)
            if not valid.any():
                return None
            return float((vals[valid] * weights[valid]).sum() / weights[valid].sum())

        expected_stats = expected_lookup.get(int(pitcher_id), {})
        batted_ball_stats = batted_ball_lookup.get(int(pitcher_id), {})
        season_counts = season_count_lookup.get(int(pitcher_id), {})
        advanced_counts = advanced_lookup.get(int(pitcher_id), {})
        whiff_percent = _weighted('whiff_percent')
        pa_total = int(weights.sum()) if weights.sum() > 0 else None
        whiffs = advanced_counts.get('whiffs')
        if whiffs is None:
            whiffs = int(round((whiff_percent * pa_total) / 100)) if whiff_percent is not None and pa_total else None

        pitchers.append({
            "player_id": int(pitcher_id),
            "name": display_name,
            "team": team,
            "position": position,
            "ba": expected_stats.get('ba', _weighted('ba')),
            "slg": expected_stats.get('slg', _weighted('slg')),
            "swings": advanced_counts.get('swings'),
            "hits": season_counts.get('hits'),
            "woba": _weighted('woba'),
            "est_ba": _weighted('est_ba'),
            "est_slg": _weighted('est_slg'),
            "est_woba": _weighted('est_woba'),
            "hard_hit_percent": batted_ball_stats.get('hard_hit_percent', _weighted('hard_hit_percent')),
            "hard_hits": batted_ball_stats.get('hard_hits'),
            "whiff_percent": whiff_percent,
            "whiffs": whiffs,
            "k_percent": _weighted('k_percent'),
            "arsenal": pitches,
        })

    pitcher_lookup = {pitcher['player_id']: pitcher for pitcher in pitchers}
    pitches_by_type: dict[str, list[dict]] = {}

    for pitcher in pitchers:
        for pitch_code, pitch_stats in pitcher['arsenal'].items():
            pitches_by_type.setdefault(pitch_code, []).append({
                'id': pitcher['player_id'],
                'stats': {
                    key: value
                    for key, value in pitch_stats.items()
                    if isinstance(value, (int, float)) or value is None
                },
            })

    for pitch_code, pitch_entries in pitches_by_type.items():
        ranked_entries = add_percentiles(pitch_entries)
        for entry in ranked_entries:
            pitch_stats = pitcher_lookup[entry['id']]['arsenal'][pitch_code]
            pitch_stats.update({
                key: value
                for key, value in entry['stats'].items()
                if key.endswith('_pct')
            })

    return pitchers


if __name__ == "__main__":
    pitchers = pitch_performance_pitcher(season=2026, qualified_only=True)
    for pitcher in pitchers:
        if pitcher['name'] == 'Kyle Bradish':
            print(json.dumps(pitcher, indent=2))
