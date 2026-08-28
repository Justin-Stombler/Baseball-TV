from ..api.pitch_data import (
    fetch_statcast_pitcher_arsenal_stats,
    fetch_statcast_pitcher_pitch_arsenal,
    fetch_statcast_pitcher_pitches,
    fetch_pitcher_team_map,
)
from ..api.player_bios import fetch_player_hand
from ..api.player_stats import fetch_pitcher_stats
from ..stats.percentiles import add_percentiles
from ..stats.qualification import filter_qualified
from data.roster import get_jersey_number
import pandas as pd
import json

##This file only builds what the pitch-arsenal card actually shows:
##  player: player_id, name, team, position, number, hand (only when include_movement=True)
##  arsenal[pitch_code]: pitch_name, pitch_usage, pitches, avg_speed_pct, spin_rate_pct, hb_in, ivb_in
##If you need more stats on the card, add a field here AND read it in src/render/pitch_arsenal.py.

##Savant's arsenal-stats endpoint (usage/speed/spin) and its raw pitch-log endpoint
##(movement/location, via _movement_by_pitch) sometimes classify the same pitch
##differently — most commonly knuckle-curve tagged "KC" in the raw log but "CU" in the
##arsenal-stats aggregation. When that happens for a given pitcher, we relabel that
##pitcher's "CU" entry to "KC" so it joins with the movement data, which is otherwise
##unreachable under "CU". This is applied per-pitcher (only when the mismatch is actually
##present), not globally, so pitchers who legitimately throw both stay untouched.
PITCH_CODE_ALIASES = {"CU": "KC"}
PITCH_NAME_OVERRIDES = {"KC": "Knuckle Curve"}


def _display_name(raw_name: str) -> str:
    """Statcast gives names as 'Last, First' — flip to 'First Last' for display."""
    if not raw_name:
        return ""
    if "," not in raw_name:
        return raw_name.strip()
    last, first = [part.strip() for part in raw_name.split(",", 1)]
    return f"{first} {last}".strip()


def _safe_fetch(fetch_fn):
    """pybaseball raises instead of returning empty data for some seasons/filters — treat as missing."""
    try:
        return fetch_fn()
    except Exception:
        return None


def _speed_and_spin_by_pitch(season: int) -> tuple[dict, dict]:
    """pybaseball returns one wide row per pitcher (columns like ff_avg_speed, sl_avg_spin).
    Reshape that into two lookups keyed by (pitcher_id, PITCH_CODE) -> value.
    """
    speed_df = _safe_fetch(lambda: fetch_statcast_pitcher_pitch_arsenal(season, minP=250, arsenal_type="avg_speed"))
    spin_df = _safe_fetch(lambda: fetch_statcast_pitcher_pitch_arsenal(season, minP=250, arsenal_type="avg_spin"))

    def reshape(df: pd.DataFrame | None, suffix: str) -> dict:
        lookup = {}
        if df is None or df.empty:
            return lookup
        suffix_token = f"_{suffix}"
        value_cols = [col for col in df.columns if col.endswith(suffix_token)]
        for _, row in df.iterrows():
            pitcher_id = row.get('pitcher')
            if pd.isna(pitcher_id):
                continue
            for col in value_cols:
                value = row.get(col)
                if pd.isna(value):
                    continue
                pitch_code = col[:-len(suffix_token)].upper()
                lookup[(int(pitcher_id), pitch_code)] = float(value)
        return lookup

    return reshape(speed_df, "avg_speed"), reshape(spin_df, "avg_spin")


def _movement_by_pitch(season: int, pitcher_id: int) -> tuple[dict, float | None]:
    """Average horizontal (hb_in) / induced-vertical (ivb_in) break in inches, plus average
    plate location (loc_x_in / loc_z_in, inches from the center of the plate at the front of
    the zone), per pitch type, for one pitcher. This hits the pitch-by-pitch Statcast
    endpoint, so only call it for the pitcher actually being rendered, not every pitcher in
    the league.

    Also returns overall (not per-pitch-type) average release extension in feet, reusing
    this same pitch log rather than a second fetch.
    """
    movement_df = fetch_statcast_pitcher_pitches(
        start_dt=f"{season}-03-01", end_dt=f"{season}-11-30", player_id=pitcher_id
    )
    if movement_df is None or movement_df.empty:
        return {}, None

    extension_ft = None
    if 'release_extension' in movement_df.columns:
        ext_mean = movement_df['release_extension'].mean()
        extension_ft = round(float(ext_mean), 1) if pd.notna(ext_mean) else None

    if not {'pitch_type', 'pfx_x', 'pfx_z'}.issubset(movement_df.columns):
        return {}, extension_ft

    has_location = {'plate_x', 'plate_z'}.issubset(movement_df.columns)
    has_release = {'release_pos_x', 'release_pos_z'}.issubset(movement_df.columns)
    value_cols = (
        ['pitch_type', 'pfx_x', 'pfx_z']
        + (['plate_x', 'plate_z'] if has_location else [])
        + (['release_pos_x', 'release_pos_z'] if has_release else [])
    )

    summary = (
        movement_df[value_cols]
        .dropna(subset=['pitch_type'])
        .groupby('pitch_type', as_index=False)
        .agg(
            hb_ft=('pfx_x', 'mean'),
            ivb_ft=('pfx_z', 'mean'),
            **({'loc_x_ft': ('plate_x', 'mean'), 'loc_z_ft': ('plate_z', 'mean')} if has_location else {}),
            **({'rel_x_ft': ('release_pos_x', 'mean'), 'rel_z_ft': ('release_pos_z', 'mean')} if has_release else {}),
        )
    )

    movement = {}
    for _, row in summary.iterrows():
        pitch_code = str(row['pitch_type']).strip().upper()
        if pitch_code:
            entry = {
                "hb_in": float(row['hb_ft']) * 12.0,
                "ivb_in": float(row['ivb_ft']) * 12.0,
            }
            if has_location and pd.notna(row.get('loc_x_ft')) and pd.notna(row.get('loc_z_ft')):
                entry["loc_x_in"] = float(row['loc_x_ft']) * 12.0
                ##plate_z is height above the ground; recenter on the average zone midpoint
                ##(~2.5ft / 30in) so 0 = the middle of the zone box, matching hb/ivb's frame.
                entry["loc_z_in"] = float(row['loc_z_ft']) * 12.0 - 30.0
            if has_release and pd.notna(row.get('rel_x_ft')) and pd.notna(row.get('rel_z_ft')):
                entry["rel_x_in"] = float(row['rel_x_ft']) * 12.0
                ##same recentering as loc_z_in so release and location share a frame.
                entry["rel_z_in"] = float(row['rel_z_ft']) * 12.0 - 30.0
            movement[pitch_code] = entry

    ##raw per-pitch plate locations for the ring render — up to 100 per pitch type, sampled
    ##evenly down the season so it's not just one outing. Same recentering as loc_z_in.
    if has_location:
        samples_by_pitch = {}
        location_rows = movement_df[['pitch_type', 'plate_x', 'plate_z']].dropna()
        for pitch_code, group in location_rows.groupby('pitch_type'):
            code = str(pitch_code).strip().upper()
            if code not in movement:
                continue
            step = max(1, len(group) // 100)
            sampled = group.iloc[::step].head(100)
            samples_by_pitch[code] = [
                (float(r['plate_x']) * 12.0, float(r['plate_z']) * 12.0 - 30.0)
                for _, r in sampled.iterrows()
            ]
    return movement, extension_ft


def _add_speed_spin_percentiles(pitchers: list[dict]) -> None:
    """Rank each pitcher's avg_speed/spin_rate against everyone else throwing the same
    pitch type (a 98mph fastball and a 98mph slider aren't compared to each other).
    Mutates `pitchers` in place, adding avg_speed_pct / spin_rate_pct to each arsenal entry.
    """
    entries_by_group: dict[str, list[dict]] = {}
    for pitcher in pitchers:
        for pitch_code, stats in pitcher['arsenal'].items():
            ##Group by the ORIGINAL classification (source_code), not the possibly-relabeled
            ##display key. Only the single pitcher rendered with include_movement=True ever
            ##gets relabeled to "KC" — every other pitcher's real curveball stays keyed "CU".
            ##Grouping by display_code would isolate a relabeled pitcher into a near-empty
            ##"KC" bucket and inflate their percentile. source_code keeps everyone who throws
            ##the same real pitch in the same comparison pool regardless of display label.
            group_key = stats.get('_percentile_group', pitch_code)
            entries_by_group.setdefault(group_key, []).append({
                'id': pitcher['player_id'],
                'pitch_code': pitch_code,
                'stats': {'avg_speed': stats['avg_speed'],
                          'spin_rate': stats['spin_rate']},
            })

    pitcher_by_id = {pitcher['player_id']: pitcher for pitcher in pitchers}
    for group_key, entries in entries_by_group.items():
        for entry in add_percentiles(entries):
            arsenal_entry = pitcher_by_id[entry['id']]['arsenal'][entry['pitch_code']]
            arsenal_entry['avg_speed_pct'] = entry['stats'].get('avg_speed_pct')
            arsenal_entry['spin_rate_pct'] = entry['stats'].get('spin_rate_pct')

    ##_percentile_group was only needed for grouping above; strip it so it doesn't leak
    ##into the final JSON output.
    for pitcher in pitchers:
        for stats in pitcher['arsenal'].values():
            stats.pop('_percentile_group', None)


def _qualified_pitcher_ids(season: int) -> set[int]:
    """Player IDs meeting the carousel's PITCHER qualification threshold (batters faced per team game)."""
    splits = fetch_pitcher_stats(season, player_pool='ALL')
    return {
        int(s['player']['id'])
        for s in filter_qualified(splits, 'PITCHER', season)
        if s.get('player', {}).get('id') is not None
    }


def generate_pitch_arsenal(
    season: int = 2026,
    qualified_only: bool = True,
    player_id: int | None = None,
    include_movement: bool = False,
) -> list[dict]:
    """Build one card's worth of data per pitcher.

    Set `player_id` to build just one pitcher (faster — skips league-wide movement fetches).
    Set `include_movement=True` to also fetch break data (hb_in/ivb_in) for the movement plot;
    this is slow per-pitcher, so it's off by default and typically combined with `player_id`.
    """
    arsenal_stats_df = fetch_statcast_pitcher_arsenal_stats(season, minPA=1)
    if arsenal_stats_df is None or arsenal_stats_df.empty:
        return []

    if qualified_only:
        ##Gate on the same batters-faced threshold the player carousel uses, so mop-up
        ##position players and 20-pitch call-ups never reach the arsenal/movement cards.
        qualified_ids = _qualified_pitcher_ids(season)
        arsenal_stats_df = arsenal_stats_df[arsenal_stats_df['player_id'].isin(qualified_ids)]
        if arsenal_stats_df.empty:
            return []

    team_df = fetch_pitcher_team_map(season=season, player_pool='QUALIFIED' if qualified_only else 'ALL')
    merged = arsenal_stats_df.merge(team_df[['player_id', 'team', 'position']], on='player_id', how='left')

    if qualified_only:
        # The qualified-only pool can be missing recent call-ups/trades — backfill from the full pool.
        all_team_df = fetch_pitcher_team_map(season=season, player_pool='ALL')
        merged = merged.merge(
            all_team_df[['player_id', 'team', 'position']].rename(
                columns={'team': 'team_all', 'position': 'position_all'}
            ),
            on='player_id', how='left',
        )
        merged['team'] = merged['team'].fillna(merged['team_all'])
        merged['position'] = merged['position'].fillna(merged['position_all'])

    target_player_id = int(player_id) if player_id is not None else None
    speed_lookup, spin_lookup = _speed_and_spin_by_pitch(season)

    pitchers = []
    for pitcher_id, group in merged.groupby('player_id', dropna=True):
        pitcher_id = int(pitcher_id)
        first = group.iloc[0]

        position = first.get('position')
        if position not in ('SP', 'RP', 'TWP'):
            continue  # this card is pitcher-only; skip position players who rarely pitch

        display_name = _display_name(first.get('last_name, first_name', ''))
        team = first.get('team') if pd.notna(first.get('team')) else first.get('team_name_alt')

        movement = {}
        hand = None
        extension_ft = None
        if include_movement and (target_player_id is None or pitcher_id == target_player_id):
            movement, extension_ft = _movement_by_pitch(season, pitcher_id)
            hand = _safe_fetch(lambda: fetch_player_hand(pitcher_id))

        arsenal = {}
        for _, row in group.iterrows():
            ##source_code is what arsenal_stats_df / speed_lookup / spin_lookup actually use
            ##(e.g. "CU") — ALWAYS look those three up with source_code, never display_code.
            source_code = str(row.get('pitch_type', '')).strip()
            pitch_usage = float(row.get('pitch_usage')) if pd.notna(row.get('pitch_usage')) else None
            if not source_code or (pitch_usage is not None and pitch_usage < 1):
                continue  # drop noise pitches thrown less than 1% of the time

            ##Only relabel if THIS pitcher's movement data actually shows the mismatch —
            ##i.e. movement has the alias target (e.g. "KC") but not source_code itself.
            ##Prevents renaming every pitcher's real CU into KC when no mismatch exists.
            display_code = source_code
            if (
                source_code in PITCH_CODE_ALIASES
                and source_code not in movement
                and PITCH_CODE_ALIASES[source_code] in movement
            ):
                display_code = PITCH_CODE_ALIASES[source_code]

            entry = {
                "pitch_name": PITCH_NAME_OVERRIDES.get(display_code, row.get('pitch_name')),
                "pitch_usage": pitch_usage,
                "pitches": int(row.get('pitches')) if pd.notna(row.get('pitches')) else None,
                "avg_speed": speed_lookup.get((pitcher_id, source_code)),
                "spin_rate": spin_lookup.get((pitcher_id, source_code)),
                "_percentile_group": source_code,
            }
            entry.update(movement.get(display_code, {}))
            arsenal[display_code] = entry

        if not arsenal:
            continue

        pitchers.append({
            "player_id": pitcher_id,
            "name": display_name,
            "team": team,
            "position": position,
            "number": get_jersey_number(display_name, pitcher_id),
            "hand": hand,
            "extension_ft": extension_ft,
            "arsenal": arsenal,
        })

    _add_speed_spin_percentiles(pitchers)

    if target_player_id is not None:
        return [pitcher for pitcher in pitchers if pitcher['player_id'] == target_player_id]

    return pitchers


if __name__ == "__main__":
    DESIRED_ID = 686973
    pitchers = generate_pitch_arsenal(
        season=2026,
        qualified_only=True,
        player_id=DESIRED_ID,
        include_movement=True,
    )

    with open("king_pitch_arsenal.json", "w") as f:
        json.dump(pitchers, f, indent=2)

    print(json.dumps(pitchers, indent=2))