##this is meant to be the 'back of the card' to the player_stats 'front of the card'
##profile is only bio
##advanced stats to be kept in separate transform but can rendered together

from ..api.player_bios import fetch_all_player_bios
from .player_stats import player_list
from data.team_abbreviations import get_team_abbreviation


def bio_list(
    season: int = 2026,
    qualified_only: bool = True,
) -> list[dict]:
    """Fetch bios only for qualified players (same pool as player_stats)."""
    qualified_players = player_list(season, qualified_only)
    qualified_map = {p['id']: p for p in qualified_players}
    raw_bios = fetch_all_player_bios(season=season)

    ##build lookup keyed by id
    bio_lookup = {b['id']: b for b in raw_bios if b.get('id') is not None}

    players = []
    for player_id, stats_player in qualified_map.items():
        bio = bio_lookup.get(player_id)
        if not bio:
            continue

        team_name = stats_player['team']
        players.append({
            'id': bio.get('id'),
            'name': bio.get('fullName'),
            'team': team_name,
            'teamAbbreviation': get_team_abbreviation(team_name),
            'primaryNumber': bio.get('primaryNumber'),
            'position': stats_player['position'],
            'age': bio.get('currentAge'),
            'height': bio.get('height'),
            'weight': bio.get('weight'),
            'batSide': bio.get('batSide', {}).get('code'),
            'pitchHand': bio.get('pitchHand', {}).get('code'),
            'birthDate': bio.get('birthDate'),
            'birthCity': bio.get('birthCity'),
            'birthStateProvince': bio.get('birthStateProvince'),
            'birthCountry': bio.get('birthCountry'),
            'mlbDebutDate': bio.get('mlbDebutDate'),
            'mlbBirthYear': bio.get('birthDate', '')[:4] if bio.get('birthDate') else None,
            'mlbDebutYear': bio.get('mlbDebutDate', '')[:4] if bio.get('mlbDebutDate') else None,
            'draftYear': bio.get('draftYear'),
            'season': season,
        })

    return players


if __name__ == "__main__":
    bios = bio_list(season=2026)
    print(f"Generated {len(bios)} player bios")
    print(bios[0])