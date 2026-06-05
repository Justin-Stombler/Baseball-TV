from ..api.expected_stats import (
    get_batter_exitvelo_barrels,
    get_hitter_expected_stats,
    get_hitter_by_name,
    get_pitcher_expected_stats,
)


def _find_player_row(df, first_name: str, last_name: str) -> dict:
    name_column = 'last_name, first_name'
    search_name = f"{last_name}, {first_name}".lower()
    matches = df[df[name_column].str.lower() == search_name]
    if matches.empty:
        matches = df[df[name_column].str.lower().str.contains(last_name.lower(), na=False)]
    if matches.empty:
        return {}
    return matches.iloc[0].to_dict()


def _find_exit_stats(exit_df, player_id: int, full_name: str) -> dict:
    if exit_df.empty:
        return {}
    if player_id is not None and player_id in exit_df['player_id'].values:
        row = exit_df[exit_df['player_id'] == player_id].iloc[0]
        return row.to_dict()
    if full_name and full_name in exit_df['last_name, first_name'].values:
        row = exit_df[exit_df['last_name, first_name'] == full_name].iloc[0]
        return row.to_dict()
    return {}


def hitter_expected_transform(
    year: int,
    first_name: str,
    last_name: str,
    min_pa: str = "q",
    min_bbe: str = "q",
) -> dict:
    """
    Get aggregated expected stats for a hitter.

    ARGUMENTS
        year: The season year (e.g., 2024)
        first_name: Player's first name
        last_name: Player's last name
        min_pa: Minimum plate appearances for expected stats. "q" = qualified.
        min_bbe: Minimum batted ball events for exit velocity/barrel rate. "q" = qualified.

    Returns dict with player's expected stats.
    """
    player_data = get_hitter_by_name(year, first_name, last_name, min_pa=min_pa)

    if not player_data:
        return {
            'player': f"{first_name} {last_name}",
            'year': year,
            'found': False,
            'stats': {}
        }

    exit_stats = get_batter_exitvelo_barrels(year, min_bbe=min_bbe)
    full_name = player_data.get('last_name, first_name', f"{last_name}, {first_name}")
    bar_stats = _find_exit_stats(exit_stats, player_data.get('player_id'), full_name)

    stats = {
        'pa': player_data.get('pa'),
        'ba': player_data.get('ba'),
        'xba': player_data.get('est_ba'),
        'slg': player_data.get('slg'),
        'xslg': player_data.get('est_slg'),
        'woba': player_data.get('woba'),
        'xwoba': player_data.get('est_woba'),
        'exit_velocity': bar_stats.get('avg_hit_speed'),
        'barrel_rate': bar_stats.get('brl_percent'),
        'batted_ball_events': bar_stats.get('attempts'),
    }

    player_name = player_data.get('last_name, first_name', f"{first_name} {last_name}")

    return {
        'player': player_name,
        'year': year,
        'found': True,
        'stats': stats
    }


def pitcher_expected_transform(
    year: int,
    first_name: str,
    last_name: str,
    min_ip: str = "q",
) -> dict:
    """
    Get aggregated expected stats for a pitcher.

    ARGUMENTS
        year: The season year (e.g., 2024)
        first_name: Player's first name
        last_name: Player's last name
        min_ip: Minimum plate appearances for opposing batters. "q" = qualified.

    Returns dict with player's expected stats.
    """
    df = get_pitcher_expected_stats(year, min_ip=min_ip)
    player_data = _find_player_row(df, first_name, last_name)

    if not player_data:
        return {
            'player': f"{first_name} {last_name}",
            'year': year,
            'found': False,
            'stats': {}
        }

    stats = {
        'pa': player_data.get('pa'),
        'ba': player_data.get('ba'),
        'xba': player_data.get('est_ba'),
        'slg': player_data.get('slg'),
        'xslg': player_data.get('est_slg'),
        'woba': player_data.get('woba'),
        'xwoba': player_data.get('est_woba'),
        'era': player_data.get('era'),
        'xera': player_data.get('xera'),
        'era_diff': player_data.get('era_minus_xera_diff'),
    }

    return {
        'player': player_data.get('last_name, first_name', f"{first_name} {last_name}"),
        'year': year,
        'found': True,
        'stats': stats,
    }


def get_top_hitters(year: int, limit: int = 10, min_pa: str = "q", min_bbe: str = "q") -> list[dict]:
    """
    Get top hitters by xwOBA for a given year.
    
    ARGUMENTS
        year: The season year
        limit: How many hitters to return
        min_pa: Minimum plate appearances. "q" = qualified.
        min_bbe: Minimum batted ball events for exit velocity/barrel rate. "q" = qualified.
    
    Returns list of dicts with player stats.
    """
    df = get_hitter_expected_stats(year, min_pa=min_pa)
    exit_df = get_batter_exitvelo_barrels(year, min_bbe=min_bbe)

    if df.empty:
        return []
    
    top = df.nlargest(limit, 'est_woba')
    
    results = []
    for _, row in top.iterrows():
        player_id = row.get('player_id')
        full_name = row.get('last_name, first_name')
        exit_row = _find_exit_stats(exit_df, player_id, full_name)
        results.append({
            'player': full_name,
            'year': year,
            'stats': {
                'pa': row.get('pa'),
                'ba': row.get('ba'),
                'xba': row.get('est_ba'),
                'slg': row.get('slg'),
                'xslg': row.get('est_slg'),
                'woba': row.get('woba'),
                'xwoba': row.get('est_woba'),
                'exit_velocity': exit_row.get('avg_hit_speed'),
                'barrel_rate': exit_row.get('brl_percent'),
                'batted_ball_events': exit_row.get('attempts'),
            }
        })
    
    return results


def get_top_pitchers(year: int, limit: int = 10, min_ip: str = "q") -> list[dict]:
    """
    Get top pitchers by xwOBA for a given year.
    
    ARGUMENTS
        year: The season year
        limit: How many pitchers to return
        min_ip: Minimum plate appearances for opposing batters. "q" = qualified.
    
    Returns list of dicts with player stats.
    """
    df = get_pitcher_expected_stats(year, min_ip=min_ip)

    if df.empty:
        return []
    
    top = df.nlargest(limit, 'est_woba')
    
    results = []
    for _, row in top.iterrows():
        results.append({
            'player': row.get('last_name, first_name'),
            'year': year,
            'stats': {
                'pa': row.get('pa'),
                'ba': row.get('ba'),
                'xba': row.get('est_ba'),
                'slg': row.get('slg'),
                'xslg': row.get('est_slg'),
                'woba': row.get('woba'),
                'xwoba': row.get('est_woba'),
                'era': row.get('era'),
                'xera': row.get('xera'),
                'era_diff': row.get('era_minus_xera_diff'),
            }
        })
    
    return results


def expected_stats_transform(
    year: int,
    min_pa: str = "q",
    min_ip: str = "q",
    min_bbe: str = "q",
) -> dict:
    """
    Get combined expected stats for hitters and pitchers.

    ARGUMENTS
        year: The season year
        min_pa: Minimum hitter plate appearances.
        min_ip: Minimum pitcher opposing PA.
        min_bbe: Minimum batted ball events for exit velocity/barrel rate.
    """
    return {
        'year': year,
        'hitters': get_top_hitters(year, min_pa=min_pa, min_bbe=min_bbe),
        'pitchers': get_top_pitchers(year, min_ip=min_ip),
    }


if __name__ == "__main__":
    import json
    
    year = 2026
    
    print(f"\n{'='*80}")
    print(f"Expected Stats Transform - {year} Season")
    print(f"{'='*80}\n")
    
    ##pull kyle bradish's expected stats
    kyle_bradish_stats = pitcher_expected_transform(year, "Kyle", "Bradish", min_ip='q')
    print("Kyle Bradish's Expected Stats:")
    print(json.dumps(kyle_bradish_stats, indent=4))