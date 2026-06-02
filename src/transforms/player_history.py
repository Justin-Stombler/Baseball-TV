from ..api.player_stats import fetch_hitter_stats, fetch_pitcher_stats
from ..stats.config import HISTORY_CONFIG
from data.team_abbreviations import get_team_abbreviation
##kind of meant ot mimic the player history tables you see on the back of a baseball card


def player_history(
    players: list[dict],
    season: int = 2026,
    count: int = 4,
    qualified_only: bool = True,
) -> dict[int, list[dict]]:
    """Return history rows keyed by player id for a list of players."""
    seasons = [season - i for i in range(count - 1, -1, -1)]
    history_by_id: dict[int, list[dict]] = {}
    player_groups = {
        "hitting": [player for player in players if player.get("position") != "P" and player.get("id") is not None],
        "pitching": [player for player in players if player.get("position") == "P" and player.get("id") is not None],
    }

    for group_name, grouped_players in player_groups.items():
        if not grouped_players:
            continue

        position = "P" if group_name == "pitching" else ""
        stat_keys = [
            stat_key
            for stat_key, stat_config in HISTORY_CONFIG["stats"].items()
            if stat_config.get("active", True)
            and (stat_config.get("type") == group_name or stat_config.get("type") == "both")
        ]

        if position == "P":
            qualified_splits = fetch_pitcher_stats(season, player_pool="QUALIFIED") if qualified_only else []
        else:
            qualified_splits = fetch_hitter_stats(season, player_pool="QUALIFIED") if qualified_only else []

        qualified_ids = {
            split["player"]["id"]
            for split in qualified_splits
            if split.get("player", {}).get("id") is not None
        }

        player_ids = {
            player["id"]
            for player in grouped_players
            if not qualified_only or player["id"] in qualified_ids
        }

        season_data = {}
        for year in seasons:
            if position == "P":
                splits = fetch_pitcher_stats(year, player_pool="ALL")
            else:
                splits = fetch_hitter_stats(year, player_pool="ALL")

            season_data[year] = {
                split["player"]["id"]: split
                for split in splits
                if split.get("player", {}).get("id") in player_ids
            }

        for player_id in player_ids:
            rows = []
            for year in seasons:
                record = season_data[year].get(player_id)
                row = {"season": year}
                # Add team abbreviation if requested
                if "team" in stat_keys:
                    team_name = record["team"]["name"] if record else None
                    row["team"] = get_team_abbreviation(team_name) if team_name else None
                for key in stat_keys:
                    if key != "team":
                        row[key] = record["stat"].get(key) if record else None
                rows.append(row)
            history_by_id[player_id] = rows

    return history_by_id


if __name__ == "__main__":
    from .player_bios import bio_list

    bios = bio_list(season=2026)
    histories = player_history(bios)
    sample = next((p for p in bios if p["name"] == "Brandon Lowe"), bios[0])
    print(sample["name"], sample["position"])
    for row in histories.get(sample["id"], []):
        print(row)
