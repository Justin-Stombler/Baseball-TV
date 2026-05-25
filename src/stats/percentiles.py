from ..transform import player_list
from .config import STAT_CONFIG

def add_percentiles(players: list[dict]) -> list[dict]:
    for stat_key, config in STAT_CONFIG.items():
        values = []

    for p in players:
        raw_value = p.get('stats', {}).get(stat_key, 0)

        try:
            value = float(raw_value)
        except (ValueError, TypeError):
            value = 0.0

        values.append(value)
        
        for p in players:
            raw = float(p['stats'].get(stat_key) or 0)
            pct = sum(1 for v in values if v <= raw) / len(values) * 100
            
            if config["ascending"]:
                pct = 100 - pct
                
            p['stats'][f'{stat_key}_pct'] = round(pct)
    
    return players

if __name__ == "__main__":
    players = player_list(season=2026, qualified_only=True)

    players_with_percentiles = add_percentiles(players)

    print(players_with_percentiles[:1])  # Print top player
