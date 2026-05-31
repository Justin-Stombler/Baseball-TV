import statsapi

def fetch_all_player_bios(season: int = 2026) -> list[dict]:
    """Fetch all player bios for MLB in a single upfront pull."""
    data = statsapi.get('sports_players', {
        'sportId': 1,
        'season': season,
    })
    return data.get('people', [])

##returns lots of useful 'back of the card' information

if __name__ == "__main__":
    bios = fetch_all_player_bios(season=2025)
    print(f"Fetched {len(bios)} bios")
    print(bios[0])
