from .api import fetch_hitter_stats, fetch_pitcher_stats

STAT_CONFIG = {
    "ERA": {"ascending": True},
    "WHIP": {"ascending": True},
    "SO": {"ascending": False},
    "OPS": {"ascending": False},
    "AVG": {"ascending": False},
    "HR": {"ascending": False},
}

def percentile_inserter (players: list[dict], stat_key: str) -> list[dict]:
    sorted_players = sorted(players, key=lambda p: p['stats'][stat_key], reverse=not STAT_CONFIG[stat_key]["ascending"])
    for i, player in enumerate(sorted_players):
        player['stats'][f'{stat_key}_perc'] = f"{((len(players) - i) / len(players) * 100):.2f}"
    return sorted_players

if __name__ == "__main__":
    hitters = fetch_hitter_stats(2026)
    pitchers = fetch_pitcher_stats(2026)
    
    hitters_with_percentiles = percentile_inserter(hitters, 'AVG')
    hitters_with_percentiles = percentile_inserter(hitters, 'OPS')
    hitters_with_percentiles = percentile_inserter(hitters, 'HR')
    pitchers_with_percentiles = percentile_inserter(pitchers, 'SO')
    pitchers_with_percentiles = percentile_inserter(pitchers, 'ERA')
    pitchers_with_percentiles = percentile_inserter(pitchers, 'WHIP')
    
    
    print(hitters_with_percentiles[:3])
    print(pitchers_with_percentiles[:3])

##ERA needs to be flipped, lower is better