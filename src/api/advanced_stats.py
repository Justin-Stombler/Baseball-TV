import statsapi


def _normalize_name(name: str) -> str:
    return (name or '').strip().lower()


def fetch_advanced_hitting(player_id: int, season: int = 2026) -> dict:
    """Fetch seasonAdvanced hitting stats for a player."""
    data = statsapi.get('stats', {
        'stats': 'seasonAdvanced',
        'group': 'hitting',
        'season': season,
        'gameType': 'R',
        'personIds': player_id,
    })
    try:
        return data['stats'][0]['splits'][0]['stat']
    except (IndexError, KeyError):
        return {}


def fetch_advanced_pitching(player_id: int, season: int = 2026) -> dict:
    """Fetch seasonAdvanced pitching stats for a player."""
    data = statsapi.get('stats', {
        'stats': 'seasonAdvanced',
        'group': 'pitching',
        'season': season,
        'gameType': 'R',
        'personIds': player_id,
    })
    try:
        return data['stats'][0]['splits'][0]['stat']
    except (IndexError, KeyError):
        return {}


def fetch_all_advanced_hitting(season: int = 2026, player_pool: str = 'ALL') -> list[dict]:
    """Fetch all seasonAdvanced hitting splits with pagination."""
    all_splits = []
    offset = 0
    limit = 500

    while True:
        data = statsapi.get('stats', {
            'stats': 'seasonAdvanced',
            'group': 'hitting',
            'season': season,
            'gameType': 'R',
            'playerPool': player_pool,
            'limit': limit,
            'offset': offset,
        })

        splits = data['stats'][0]['splits']
        if not splits:
            break

        all_splits.extend(splits)

        if len(splits) < limit:
            break

        offset += limit

    return all_splits


def fetch_all_advanced_pitching(season: int = 2026, player_pool: str = 'ALL') -> list[dict]:
    """Fetch all seasonAdvanced pitching splits with pagination."""
    all_splits = []
    offset = 0
    limit = 500

    while True:
        data = statsapi.get('stats', {
            'stats': 'seasonAdvanced',
            'group': 'pitching',
            'season': season,
            'gameType': 'R',
            'playerPool': player_pool,
            'limit': limit,
            'offset': offset,
        })

        splits = data['stats'][0]['splits']
        if not splits:
            break

        all_splits.extend(splits)

        if len(splits) < limit:
            break

        offset += limit

    return all_splits


def fetch_all_advanced_hitting_by_id(season: int = 2026, player_pool: str = 'ALL') -> dict[int, dict]:
    """Fetch all advanced hitting splits keyed by player id."""
    splits = fetch_all_advanced_hitting(season=season, player_pool=player_pool)
    return {
        s['player']['id']: s
        for s in splits
        if s.get('player', {}).get('id') is not None
    }


def fetch_all_advanced_pitching_by_id(season: int = 2026, player_pool: str = 'ALL') -> dict[int, dict]:
    """Fetch all advanced pitching splits keyed by player id."""
    splits = fetch_all_advanced_pitching(season=season, player_pool=player_pool)
    return {
        s['player']['id']: s
        for s in splits
        if s.get('player', {}).get('id') is not None
    }


def fetch_all_advanced_hitting_by_name(season: int = 2026, player_pool: str = 'ALL') -> dict[str, list[dict]]:
    """Fetch all advanced hitting splits keyed by normalized full name."""
    out: dict[str, list[dict]] = {}
    for split in fetch_all_advanced_hitting(season=season, player_pool=player_pool):
        key = _normalize_name(split.get('player', {}).get('fullName', ''))
        if not key:
            continue
        out.setdefault(key, []).append(split)
    return out


def fetch_all_advanced_pitching_by_name(season: int = 2026, player_pool: str = 'ALL') -> dict[str, list[dict]]:
    """Fetch all advanced pitching splits keyed by normalized full name."""
    out: dict[str, list[dict]] = {}
    for split in fetch_all_advanced_pitching(season=season, player_pool=player_pool):
        key = _normalize_name(split.get('player', {}).get('fullName', ''))
        if not key:
            continue
        out.setdefault(key, []).append(split)
    return out

if __name__ == "__main__":
    hitters = fetch_all_advanced_hitting(season=2025)
    pitchers = fetch_all_advanced_pitching(season=2025)
    print(f"Fetched {len(hitters)} advanced hitting splits")
    print(f"Fetched {len(pitchers)} advanced pitching splits")
    print("Example advanced hitting split:", hitters[0] if hitters else "No data")
    print("Example advanced pitching split:", pitchers[0] if pitchers else "No data")