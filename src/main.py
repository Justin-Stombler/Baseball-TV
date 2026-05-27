from .transforms.player_stats import player_list
from .transforms.leaderboard import generate_leaderboard
from .render.player_stats import render_player_stats
from .render.leaderboard import render_leaderboard
from .push import push, delete
from .stats.config import STAT_CONFIG
import random
import time

def get_random_player() -> dict:
    """Get a random player from the combined list of hitters and pitchers."""
    return random.choice(player_list())

def get_random_stat() -> str:
    """Get a random stat from the available stats in the config."""
    return random.choice(list(STAT_CONFIG.keys()))

def get_random_league() -> str:
    """Get a random league."""
    return random.choice(['AL', 'NL'])

if __name__ == "__main__":
    previous = None

    while True:
        stat = get_random_stat()
        league = get_random_league()
        leaderboard = generate_leaderboard(season=2026, league=league, stat=stat)
        img_bytes = render_leaderboard(leaderboard, stat=stat, league=league)
        current_filename = push(img_bytes)
        print(f"pushed {current_filename} -> stat={stat} league={league}")
        if previous:
            delete(previous)
        previous = current_filename
        time.sleep(10)

    # while True:
    #     player = get_random_player()
    #     image = render_player_stats(player)
    #     push(image, filename=f"{player['name'].replace(' ', '_')}.jpg")
    #     if previous:
    #         delete(previous)
    #     previous = f"{player['name'].replace(' ', '_')}.jpg"
    #     time.sleep(5)