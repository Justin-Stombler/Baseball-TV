from ..api.statcast_pitching import (
    fetch_statcast_batter_pitch_arsenal,
    fetch_hitter_team_map,
)
import pandas as pd
import json


def _display_name(raw_name: str) -> str:
    if not raw_name:
        return ""
    if "," not in raw_name:
        return raw_name.strip()
    last, first = [part.strip() for part in raw_name.split(",", 1)]
    return f"{first} {last}".strip()


def pitch_performance_hitter(season: int = 2026, qualified_only: bool = True) -> list[dict]:
    """Transform hitter performance against pitch types into a usable format.
    
    Returns list of hitters with player_id, name, team, position, and a dict of pitches
    showing performance (BA, SLG, WOBA, etc.) against each pitch type.
    All pitch types included (min_pa=1) so pitch_usage reflects full pitch exposure.
    """
    min_pa = 1

    batter_stats_df = fetch_statcast_batter_pitch_arsenal(season, minPA=min_pa)
    if batter_stats_df is None or batter_stats_df.empty:
        return []

    team_df = fetch_hitter_team_map(season=season, player_pool='QUALIFIED' if qualified_only else 'ALL')
    merged = batter_stats_df.merge(
        team_df[['player_id', 'team', 'position']],
        on='player_id',
        how='left'
    )

    if qualified_only:
        all_team_df = fetch_hitter_team_map(season=season, player_pool='ALL')
        merged = merged.merge(
            all_team_df[['player_id', 'team', 'position']].rename(
                columns={'team': 'team_all', 'position': 'position_all'}
            ),
            on='player_id',
            how='left'
        )
        merged['team'] = merged['team'].fillna(merged['team_all'])
        merged['position'] = merged['position'].fillna(merged['position_all'])

    hitters = []

    for player_id, group in merged.groupby('player_id', dropna=True):
        first = group.iloc[0]
        display_name = _display_name(first.get('last_name, first_name', ''))
        team = first.get('team') if pd.notna(first.get('team')) else first.get('team_name_alt')
        position = first.get('position')

        pitches = {}
        for _, row in group.iterrows():
            pitch_code = str(row.get('pitch_type', '')).strip()
            if not pitch_code:
                continue

            pitches[pitch_code] = {
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

        if not pitches:
            continue

        weights = pd.to_numeric(group['pa'], errors='coerce').fillna(0)

        def _weighted(col: str):
            vals = pd.to_numeric(group[col], errors='coerce')
            valid = vals.notna() & (weights > 0)
            if not valid.any():
                return None
            return float((vals[valid] * weights[valid]).sum() / weights[valid].sum())

        hitters.append({
            "player_id": int(player_id),
            "name": display_name,
            "team": team,
            "position": position,
            "est_ba": _weighted('est_ba'),
            "est_slg": _weighted('est_slg'),
            "est_woba": _weighted('est_woba'),
            "hard_hit_percent": _weighted('hard_hit_percent'),
            "arsenal": pitches,
        })

    return hitters


if __name__ == "__main__":
    hitters = pitch_performance_hitter(season=2026, qualified_only=False)
    for hitter in hitters:
        if hitter['name'] == 'Dylan Moore':
            print(json.dumps(hitter, indent=2))
            break
