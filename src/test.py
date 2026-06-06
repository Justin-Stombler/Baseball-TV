import random
import time
import re

from src.config import DISPLAY_CONFIG
from src.push import push, delete
from src.render.leaderboard import render_leaderboard
from src.render.player_profiles import render_player_profiles
from src.render.player_stats import render_player_stats
from src.render.batted_ball_profile import render_batted_ball_profile
from src.render.statcast_data import render_statcast_data
from src.render.stings import render_sting, stings
from src.stats.config import STAT_CONFIG
from src.transforms.leaderboard import generate_leaderboard
from src.transforms.player_bios import bio_list
from src.transforms.player_history import player_history
from src.transforms.player_stats import player_list
from src.transforms.batted_ball_profile import player_list as batted_ball_player_list
from src.transforms.statcast_data import expected_stats_list


def display(image: bytes, duration: int, previous: str | None, filename: str | None = None) -> str:
    """Push image, delete previous, wait duration. Returns current filename."""
    current = push(image, filename=filename)
    if previous:
        delete(previous)
    time.sleep(duration)
    return current


def run_player_stats_test(previous: str | None) -> str:
    cfg = DISPLAY_CONFIG["player_stats"]
    players = player_list()
    player = random.choice(players)
    current = display(render_player_stats(player), cfg["duration"], previous=previous)
    print("Pushed mode: player_stats")
    return current


def run_player_profiles_test(previous: str | None) -> str | None:
    cfg = DISPLAY_CONFIG["player_profiles"]
    history_count = cfg.get("seasons")

    players = player_list()
    bios = bio_list()
    bio_by_id = {b["id"]: b for b in bios}
    player = random.choice(players)

    bio = bio_by_id.get(player["id"])
    if not bio:
        print("No matching bio found for selected player. Try again.")
        return previous

    history_dict = player_history([bio], count=history_count)
    bio = {**bio, "history": history_dict.get(player["id"], [])}
    current = display(render_player_profiles(bio), cfg["duration"], previous=previous)
    print("Pushed mode: player_profiles")
    return current


def run_leaderboard_test(previous: str | None) -> str:
    cfg = DISPLAY_CONFIG["leaderboard"]
    active_stats = [k for k, v in STAT_CONFIG.items() if v.get("active", True)]
    stat = random.choice(active_stats)
    league = random.choice(cfg["leagues"])

    leaderboard = generate_leaderboard(league=league, stat=stat)
    current = display(
        render_leaderboard(leaderboard, stat=stat, league=league),
        cfg["duration"],
        previous=previous,
        filename=f"{stat}_{league}.jpg",
    )
    print(f"Pushed mode: leaderboard ({league}, {stat})")
    return current

def run_batted_ball_profile_test(previous: str | None) -> str:
    cfg = DISPLAY_CONFIG["batted_ball_profile"]
    players = batted_ball_player_list()
    player = random.choice(players)
    current = display(render_batted_ball_profile(player), cfg["duration"], previous=previous)
    print("Pushed mode: batted_ball_profile")
    return current

def run_sting_test(previous: str | None) -> str:
    cfg = DISPLAY_CONFIG["stings"]
    sting_text = random.choice(stings)
    current = display(render_sting(sting_text), cfg["duration"], previous=previous)
    print("Pushed mode: stings")
    return current

def run_statcast_data_test(previous: str | None) -> str:
    cfg = DISPLAY_CONFIG["statcast"]
    players = expected_stats_list()
    player = random.choice(players)
    current = display(render_statcast_data(player), cfg["duration"], previous=previous)
    print("Pushed mode: statcast")
    return current

def choose_mode() -> str:
    while True:
        print("Choose a mode to test push output:")
        print("1) player_stats")
        print("2) player_profiles")
        print("3) leaderboard")
        print("4) batted_ball_profile")
        print("5) statcast")
        print("6) stings")
        raw_choice = input("Enter 1, 2, 3, 4, 5, or 6: ").strip()

        match = re.search(r"[123456]", raw_choice)
        if match:
            return match.group(0)

        print("Invalid choice. Enter 1, 2, 3, 4, 5, or 6.")


def main() -> None:
    choice = choose_mode()
    previous = None

    while True:
        if choice == "1":
            previous = run_player_stats_test(previous)
        elif choice == "2":
            previous = run_player_profiles_test(previous)
        elif choice == "3":
            previous = run_leaderboard_test(previous)
        elif choice == "4":
            previous = run_batted_ball_profile_test(previous)
        elif choice == "5":
            previous = run_statcast_data_test(previous)
        elif choice == "6":
            previous = run_sting_test(previous)

        # SLEEP_BETWEEN_PUSHES: comment out to remove the pause
        time.sleep(5)


if __name__ == "__main__":
    main()
