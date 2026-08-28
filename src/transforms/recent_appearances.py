from ..api.game_data import fetch_player_recent_games
from ..stats.config import RECENT_APPEARANCES_CONFIG


def recent_appearances_columns(group: str) -> list[tuple[str, str]]:
    """Return the (stat_key, label) columns active for this group, sorted by "order"."""
    active_stats = [
        (stat_key, stat_config)
        for stat_key, stat_config in RECENT_APPEARANCES_CONFIG["stats"].items()
        if stat_config.get("active", True) and stat_config.get("type") in (group, "both")
    ]
    active_stats.sort(key=lambda item: item[1].get("order", 0))
    return [(stat_key, stat_config["label"]) for stat_key, stat_config in active_stats]


def recent_appearances(player: dict, count: int | None = None, season: int = 2026) -> list[dict]:
    """Build a list of the player's last `count` games, one row per game,
    following the same shape as the player-profile history table but keyed
    to individual games instead of seasons."""
    count = count if count is not None else RECENT_APPEARANCES_CONFIG["games"]
    group = "pitching" if player.get("position") in ("SP", "RP", "P", "TWP") else "hitting"
    columns = recent_appearances_columns(group)
    games = fetch_player_recent_games(player["id"], group=group, season=season, count=count)

    rows = []
    for game in games:
        stats = game.get("stats", {})
        row = {"date": game.get("date"), "opponent": game.get("opponent")}
        for key, _label in columns:
            row[key] = stats.get(key)
        rows.append(row)
    return rows


if __name__ == "__main__":
    import random
    from .player_stats import player_list

    sample_player = random.choice(player_list())
    for row in recent_appearances(sample_player):
        print(row)
