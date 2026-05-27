from .config import STAT_CONFIG


def add_percentiles(players: list[dict]) -> list[dict]:
    """Add percentile fields to each player's stats."""
    for stat_key, config in STAT_CONFIG.items():
        valid_players = [player for player in players if player['stats'].get(stat_key) is not None]
        if not valid_players:
            continue

        reverse = not config.get('ascending', False)
        sorted_players = sorted(valid_players, key=lambda p: p['stats'][stat_key], reverse=reverse)
        total = len(sorted_players)

        for rank, player in enumerate(sorted_players):
            pct = round((total - rank) / total * 100, 2)
            player['stats'][f'{stat_key}_pct'] = pct

    return players