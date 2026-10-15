from ..api.game_data import fetch_player_recent_games
from ..stats.config import RECENT_APPEARANCES_CONFIG


def recent_appearances_columns(group: str) -> list[tuple[str, str]]:
    """Return the (stat_key, label) columns for this group, in display order."""
    return list(RECENT_APPEARANCES_CONFIG[group])


def recent_appearances(player: dict, count: int | None = None, season: int = 2026) -> list[dict]:
    """Build a list of the player's last `count` games, one row per game,
    following the same shape as the player-profile history table but keyed
    to individual games instead of seasons."""
    count = count if count is not None else RECENT_APPEARANCES_CONFIG["games"]
    season = player.get("season", season)
    group = "pitching" if player.get("position") in ("SP", "RP", "P", "TWP") else "hitting"
    columns = recent_appearances_columns(group)
    games = fetch_player_recent_games(player["id"], group=group, season=season, count=count)

    rows = []
    for game in games:
        stats = game.get("stats", {})
        row = {
            "date": game.get("date"),
            "opponent": game.get("opponent"),
            "is_home": game.get("is_home"),
            "game_type": game.get("game_type"),
            "round": game.get("round"),
        }
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
