from transform import hitter_transform
from transform import pitcher_transform
import random

hitters = hitter_transform(qualified_only=True)
pitchers = pitcher_transform(qualified_only=True)

players = hitters + pitchers

def get_random_player() -> dict:
    """Get a random player from the combined list of hitters and pitchers."""
    return random.choice(players)

if __name__ == "__main__":
    random_player = get_random_player()
    print(f"Random Player: {random_player['name']} - {random_player['team']} - {random_player['position']}")
    print(f"Stats: {random_player['stats']}")