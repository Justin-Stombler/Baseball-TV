import statsapi

def fetch_all_player_bios(season: int = 2026) -> list[dict]:
    """Fetch all player bios for MLB in a single upfront pull."""
    data = statsapi.get('sports_players', {
        'sportId': 1,
        'season': season,
    })
    return data.get('people', [])


def fetch_player_hand(player_id: int) -> str | None:
    """Fetch a single player's throwing hand ('R'/'L') by id. Lightweight — a single-player
    call, not a season-wide pull — so it's fine to use per-card instead of per-league.
    """
    data = statsapi.get('people', {'personIds': player_id})
    people = data.get('people', [])
    if not people:
        return None
    return people[0].get('pitchHand', {}).get('code')

##returns lots of useful 'back of the card' information

if __name__ == "__main__":
    bios = fetch_all_player_bios(season=2025)
    print(f"Fetched {len(bios)} bios")
    print(bios[0])
