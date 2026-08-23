##roster lookups, backed by roster.json (the current 40-man rosters)
##single source of truth for "is this player still rostered" + "what team/number do they wear now"
##anything using team or jersey number off a stats-api split should go through here instead,
##since those splits can be stale after a trade/DFA (they don't update mid-season)

import json
from pathlib import Path

with open(Path(__file__).parent / "roster.json") as f:
    _roster_list = json.load(f)

ROSTERS_BY_ID = {p['id']: p for p in _roster_list if p.get('id') is not None}
ROSTERS_BY_NAME = {p['name']: p for p in _roster_list}


def is_rostered(player_id: int) -> bool:
    """True if this player is on a current 40-man roster."""
    return player_id in ROSTERS_BY_ID


def get_team(player_id: int) -> str | None:
    """Current roster team name for a player. Returns None if not rostered."""
    return ROSTERS_BY_ID.get(player_id, {}).get('team')


def get_jersey_number(full_name: str, player_id: int):
    """Get jersey number from roster.json, by id first then name. Returns None if the player isn't listed."""
    if player_id in ROSTERS_BY_ID:
        return ROSTERS_BY_ID[player_id].get('number')
    return ROSTERS_BY_NAME.get(full_name, {}).get('number')

if __name__ == "__main__":
    print(get_team(663460), get_jersey_number("Kris Bubic", 663460))
