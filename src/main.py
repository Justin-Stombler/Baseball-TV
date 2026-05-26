from .transforms.player_stats import player_list
from .render.player_stats import render_player_stats
from .push import push, delete
import random
import time

def get_random_player() -> dict:
    """Get a random player from the combined list of hitters and pitchers."""
    return random.choice(player_list())

if __name__ == "__main__":
    previous = None

    while True:
        player = get_random_player()
        image = render_player_stats(player)
        push(image, filename=f"{player['name'].replace(' ', '_')}.jpg")
        if previous:
            delete(previous)
        previous = f"{player['name'].replace(' ', '_')}.jpg"
        time.sleep(5)