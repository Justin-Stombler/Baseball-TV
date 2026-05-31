from ..api.player_stats import fetch_hitter_stats, fetch_pitcher_stats
from ..stats.config import HISTORY_CONFIG
##kind of meant ot mimic the player history tables you see on the back of a baseball card



def history_seasons(season: int = 2026, count: int = 4) -> list[int]:
    """Return the last `count` seasons ending at `season` in ascending order."""
    return [season - i for i in range(count - 1, -1, -1)]


def player_history_by_id(
    player_id: int,
    position: str,
    season: int = 2026,
    count: int = 4,
    qualified_only: bool = True,
) -> list[dict]:
    """Return a small history table for a single player by ID.
    
    If qualified_only=True, fetches ALL data but restricts to players 
    currently in the QUALIFIED pool (at the given season).
    This allows currently-qualified players to have history from years
    when they may not have been qualified.
    """
    # Build set of currently-qualified player IDs if restricting
    qualified_player_ids = set()
    if qualified_only:
        current_season_data = fetch_hitter_stats(season, player_pool="QUALIFIED") if position != "P" else fetch_pitcher_stats(season, player_pool="QUALIFIED")
        qualified_player_ids = {split["player"]["id"] for split in current_season_data}
        # If player not currently qualified, return empty history
        if player_id not in qualified_player_ids:
            return []
    
    # Always fetch from ALL pool to get complete historical data
    player_pool = "ALL"
    seasons = history_seasons(season=season, count=count)
    position_type = "pitching" if position == "P" else "hitting"
    stat_keys = [
        stat_key
        for stat_key, stat_config in HISTORY_CONFIG["stats"].items()
        if stat_config.get("active", True)
        and (stat_config.get("type") == position_type or stat_config.get("type") == "both")
    ]

    history = []
    for year in seasons:
        if position == "P":
            splits = fetch_pitcher_stats(year, player_pool=player_pool)
        else:
            splits = fetch_hitter_stats(year, player_pool=player_pool)

        record = next((split for split in splits if split["player"]["id"] == player_id), None)
        row = {"season": year}
        for key in stat_keys:
            row[key] = record["stat"].get(key) if record else None
        history.append(row)

    return history


def player_history(
    player: dict,
    season: int = 2026,
    count: int = 4,
    qualified_only: bool = True,
) -> list[dict]:
    """Return a small history table for a profile-style player dict."""
    return player_history_by_id(
        player_id=player["id"],
        position=player.get("position", ""),
        season=season,
        count=count,
        qualified_only=qualified_only,
    )


if __name__ == "__main__":
    from .player_bios import bio_list

    bios = bio_list(season=2026)
    sample = next((p for p in bios if p["name"] == "Brandon Lowe"), bios[0])
    history = player_history(sample)
    print(sample["name"], sample["position"])
    for row in history:
        print(row)
