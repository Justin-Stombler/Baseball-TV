##Classifies pitchers as starters (SP) or relievers (RP) using gamesStarted/gamesPitched.
##Two-way players (abbreviation 'TWP') are passed through unchanged.

from ..api.player_stats import fetch_pitcher_stats

ROLE_THRESHOLD = 0.5


def classify_role(games_started, games_pitched, default: str = 'RP') -> str:
    """Return 'SP' when gamesStarted/gamesPitched >= ROLE_THRESHOLD, else 'RP'."""
    try:
        gs = float(games_started or 0)
        gp = float(games_pitched or 0)
    except (TypeError, ValueError):
        return default
    if gp <= 0:
        return default
    return 'SP' if (gs / gp) >= ROLE_THRESHOLD else 'RP'


def pitcher_position(split: dict) -> str:
    """Return 'TWP', 'SP', or 'RP' for a statsapi pitcher stat split (needs gamesStarted/gamesPitched in split['stat']).

    Splits whose true fielding position isn't 'P'/'TWP' (e.g. a position player's mop-up
    pitching appearance) are returned unchanged instead of being classified as SP/RP.
    """
    abbreviation = split.get('position', {}).get('abbreviation')
    if abbreviation == 'TWP':
        return 'TWP'
    if abbreviation not in (None, 'P'):
        return abbreviation
    stat = split.get('stat', {})
    return classify_role(stat.get('gamesStarted'), stat.get('gamesPitched'))


def build_role_lookup(season: int = 2026) -> dict[int, str]:
    """Map player_id -> 'SP'/'RP'/'TWP', for splits that lack gamesStarted/gamesPitched of their own (e.g. seasonAdvanced)."""
    lookup = {}
    for split in fetch_pitcher_stats(season, player_pool='ALL'):
        player_id = split.get('player', {}).get('id')
        if player_id is None:
            continue
        lookup[player_id] = pitcher_position(split)
    return lookup
