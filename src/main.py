from .transforms.player_stats import player_list
from .transforms.leaderboard import generate_leaderboard
from .render.player_stats import render_player_stats
from .render.leaderboard import render_leaderboard
from .push import push, delete
from .config import DISPLAY_CONFIG
from .stats.config import STAT_CONFIG
import random
import time

def get_random_player() -> dict:
    """Get a random player from the combined list of hitters and pitchers."""
    return random.choice(player_list())

def get_random_stat() -> str:
    """Get a random stat from the active stats in the config."""
    active_stats = [k for k, v in STAT_CONFIG.items() if v.get("active", True)]
    return random.choice(active_stats)

def display(image: bytes, duration: int, previous: str | None, filename: str = None) -> str:
    """Push image, delete previous, wait duration. Returns current filename."""
    current = push(image, filename=filename)
    if previous:
        delete(previous)
    time.sleep(duration)
    return current

if __name__ == "__main__":
    ps = DISPLAY_CONFIG["player_stats"]
    lb = DISPLAY_CONFIG["leaderboard"]
    previous = None

    while True:
        for _ in range(ps["count"]):
            player = get_random_player()
            previous = display(render_player_stats(player), ps["duration"], previous)

        for _ in range (lb["count"]):
            stat = get_random_stat()
            for league in lb["leagues"]:
                leaderboard = generate_leaderboard(league=league, stat=stat)
                previous = display(render_leaderboard(leaderboard, stat=stat, league=league), lb["duration"], previous, filename=f"{stat}_{league}.jpg")