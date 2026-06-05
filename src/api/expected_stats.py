from typing import Optional


def _get_pybaseball():
    import pybaseball
    return pybaseball


def enable_pybaseball_cache():
    """Enable pybaseball disk caching for Statcast requests."""
    pyb = _get_pybaseball()
    if hasattr(pyb, "cache"):
        pyb.cache.enable()


def disable_pybaseball_cache():
    """Disable pybaseball disk caching."""
    pyb = _get_pybaseball()
    if hasattr(pyb, "cache"):
        pyb.cache.disable()


def fetch_statcast_all(start_dt: str, end_dt: str, team: Optional[str] = None, verbose: bool = False, parallel: bool = True):
    """Fetch Statcast event rows for the full date range."""
    pyb = _get_pybaseball()
    return pyb.statcast(start_dt, end_dt, team=team, verbose=verbose, parallel=parallel)


def fetch_statcast_hitter(player_id: int, start_dt: Optional[str] = None, end_dt: Optional[str] = None):
    """Fetch Statcast event data for a single hitter by player_id."""
    pyb = _get_pybaseball()
    return pyb.statcast_batter(start_dt, end_dt, player_id=player_id)


def fetch_statcast_pitcher(player_id: int, start_dt: Optional[str] = None, end_dt: Optional[str] = None):
    """Fetch Statcast event data for a single pitcher by player_id."""
    pyb = _get_pybaseball()
    return pyb.statcast_pitcher(start_dt, end_dt, player_id=player_id)


if __name__ == "__main__":
    start_dt = "2025-03-28"
    end_dt = "2025-04-05"

    fetch_statcast_all(start_dt, end_dt, verbose=True)

    player_id = 592450  # Example: Mike Trout
    print(f"\nFetching hitter Statcast for player_id={player_id}...")
    hitter_data = fetch_statcast_hitter(player_id, start_dt, end_dt)
    print(hitter_data.head())

    player_id = 605118  # Example: Gerrit Cole
    print(f"\nFetching pitcher Statcast for player_id={player_id}...")
    pitcher_data = fetch_statcast_pitcher(player_id, start_dt, end_dt)
    print(pitcher_data.head())