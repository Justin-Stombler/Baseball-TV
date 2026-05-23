from mlb_data import get_hitter_stats, get_pitcher_stats

def percentile_inserter (players: list[dict], stat_key: str) -> list[dict]:
    sorted_players = sorted(players, key=lambda p: p['stats'][stat_key], reverse=True)
    for i, player in enumerate(sorted_players):
        player['stats'][f'{stat_key}_perc'] = f"{((len(players) - i) / len(players) * 100):.2f}"
    return sorted_players

if __name__ == "__main__":
    hitters = get_hitter_stats()
    pitchers = get_pitcher_stats()
    
    hitters_with_percentiles = percentile_inserter(hitters, 'AVG')
    hitters_with_percentiles = percentile_inserter(hitters, 'OPS')
    hitters_with_percentiles = percentile_inserter(hitters, 'HR')
    pitchers_with_percentiles = percentile_inserter(pitchers, 'IP')
    pitchers_with_percentiles = percentile_inserter(pitchers, 'ERA')
    pitchers_with_percentiles = percentile_inserter(pitchers, 'WHIP')
    
    
    print(hitters_with_percentiles[:3])
    print(pitchers_with_percentiles[:3])

##ERA needs to be flipped, lower is better