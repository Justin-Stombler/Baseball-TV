from ..api.expected_stats import fetch_statcast_hitter, fetch_statcast_pitcher
import pandas as pd

def hitter_statcast_transform(player_id: int, start_dt: str, end_dt: str) -> list[dict]:
    """Transform raw Statcast data for a hitter into display-ready format."""
    df = fetch_statcast_hitter(player_id, start_dt, end_dt)
    
    if df is None or df.empty:
        return []

    events = []
    for _, row in df.iterrows():
        events.append({
            'player_id': player_id,
            'date': row.get('game_date'),
            'event': row.get('events'),
            'description': row.get('des'),
            'stats': {
                'exit_velocity': row.get('launch_speed'),
                'launch_angle': row.get('launch_angle'),
                'hit_distance': row.get('hit_distance_sc'),
                'xba': row.get('estimated_ba_using_speedangle'),
                'barrel': row.get('barrel'),
            }
        })

    return events


def pitcher_statcast_transform(player_id: int, start_dt: str, end_dt: str) -> list[dict]:
    """Transform raw Statcast data for a pitcher into display-ready format."""
    df = fetch_statcast_pitcher(player_id, start_dt, end_dt)

    if df is None or df.empty:
        return []

    pitches = []
    for _, row in df.iterrows():
        pitches.append({
            'player_id': player_id,
            'date': row.get('game_date'),
            'pitch_type': row.get('pitch_type'),
            'stats': {
                'velocity': row.get('release_speed'),
                'spin_rate': row.get('release_spin_rate'),
                'extension': row.get('release_extension'),
                'induced_vbreak': row.get('pfx_z'),
                'hbreak': row.get('pfx_x'),
            }
        })

    return pitches


if __name__ == "__main__":
    trout = hitter_statcast_transform(592450, "2025-03-28", "2025-04-05")
    print(trout[:3])

    cole = pitcher_statcast_transform(605118, "2025-03-28", "2025-04-05")
    print(cole[:3])