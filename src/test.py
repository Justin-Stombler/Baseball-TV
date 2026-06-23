import random
import time
import re

from src.config import DISPLAY_CONFIG
from src.push import push, delete
from src.render.leaderboard import render_leaderboard
from src.render.player_profiles import render_player_profiles
from src.render.player_stats import render_player_stats
from src.render.batted_ball_profile import render_batted_ball_profile
from src.render.statcast_batting import render_statcast_data
from src.render.stings import render_sting, stings
from src.render.team_leaderboard import render_team_leaderboard
from src.render.pitch_performance import render_pitch_performance
from src.render.division_standings import render_division_standings
from src.render.wildcard_standings import render_wildcard_standings
from src.stats.config import STAT_CONFIG
from src.transforms.leaderboard import generate_leaderboard
from src.transforms.player_bios import bio_list
from src.transforms.player_history import player_history
from src.transforms.player_stats import player_list
from src.transforms.batted_ball_profile import player_list as batted_ball_player_list
from src.transforms.statcast_batting import expected_stats_list
from src.transforms.team_leaderboard import generate_team_leaderboard, get_available_teams
from src.transforms.pitch_performance_pitcher import pitch_performance_pitcher
from src.transforms.pitch_performance_hitter import pitch_performance_hitter
from src.transforms.standings import generate_division_standings, generate_wild_card_standings



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

def run_team_leaderboard_test(previous: str | None) -> str:
    cfg = DISPLAY_CONFIG["team_leaderboard"]
    active_stats = [k for k, v in STAT_CONFIG.items() if v.get("team_leaderboard_active", True)]
    stat = random.choice(active_stats)
    teams = get_available_teams(stat=stat)
    if not teams:
        raise RuntimeError(f"No teams available for stat '{stat}'.")
    team = random.choice(teams)

    leaderboard = generate_team_leaderboard(team=team, stat=stat)
    current = display(
        render_team_leaderboard(leaderboard, stat=stat, team=team),
        cfg["duration"],
        previous=previous,
        filename=f"team__{stat}.jpg",
    )
    print(f"Pushed mode: team_leaderboard ({team}, {stat})")
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

def run_statcast_batting_test(previous: str | None) -> str:
    cfg = DISPLAY_CONFIG["statcast_batting"]
    players = expected_stats_list()
    player = random.choice(players)
    current = display(render_statcast_data(player), cfg["duration"], previous=previous)
    print("Pushed mode: statcast_batting")
    return current

def run_division_standings_test(previous: str | None) -> str:
    cfg = DISPLAY_CONFIG["division_standings"]
    next_league = getattr(run_division_standings_test, "_next_league", "AL")
    divisions = ["East", "Central", "West"]

    current = previous
    for division in divisions:
        standings = generate_division_standings(league=next_league, division=division)
        current = display(
            render_division_standings(standings=standings, division=division, league=next_league),
            cfg["duration"],
            previous=current,
        )

    run_division_standings_test._next_league = "NL" if next_league == "AL" else "AL"
    print(f"Pushed mode: division_standings ({next_league} East/Central/West)")
    return current


def run_wildcard_standings_test(previous: str | None) -> str:
    cfg = DISPLAY_CONFIG["wildcard_standings"]
    next_league = getattr(run_wildcard_standings_test, "_next_league", "AL")

    standings = generate_wild_card_standings(league=next_league)
    current = display(
        render_wildcard_standings(standings=standings, league=next_league),
        cfg["duration"],
        previous=previous,
    )

    run_wildcard_standings_test._next_league = "NL" if next_league == "AL" else "AL"
    print(f"Pushed mode: wildcard_standings ({next_league})")
    return current

def run_pitch_performance_test(previous: str | None) -> str:
    cfg = DISPLAY_CONFIG["pitch_performance"]
    hitters = pitch_performance_hitter()
    pitchers = pitch_performance_pitcher()

    if not hitters and not pitchers:
        print("No pitch performance data available for hitters or pitchers. Try again.")
        return previous

    # Alternate so both datasets are exercised during test runs.
    next_group = getattr(run_pitch_performance_test, "_next_group", "hitter")
    if next_group == "hitter" and hitters:
        selected_group = "hitter"
        player = random.choice(hitters)
        run_pitch_performance_test._next_group = "pitcher"
    elif pitchers:
        selected_group = "pitcher"
        player = random.choice(pitchers)
        run_pitch_performance_test._next_group = "hitter"
    else:
        selected_group = "hitter"
        player = random.choice(hitters)
        run_pitch_performance_test._next_group = "pitcher"

    current = display(render_pitch_performance(player), cfg["duration"], previous=previous)
    print(f"Pushed mode: pitch_performance ({selected_group})")
    return current

def choose_mode() -> str:
    while True:
        print("Choose a mode to test push output:")
        print("1) player_stats")
        print("2) player_profiles")
        print("3) leaderboard")
        print("4) team_leaderboard")
        print("5) batted_ball_profile")
        print("6) statcast_batting")
        print("7) pitch_performance")
        print("8) division_standings")
        print("9) wildcard_standings")
        print("10) stings")
        raw_choice = input("Enter 1, 2, 3, 4, 5, 6, 7, 8, 9, or 10: ").strip()

        if raw_choice in {"1", "2", "3", "4", "5", "6", "7", "8", "9", "10"}:
            return raw_choice

        print("Invalid choice. Please enter a valid value.")


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
            previous = run_team_leaderboard_test(previous)
        elif choice == "5":
            previous = run_batted_ball_profile_test(previous)
        elif choice == "6":
            previous = run_statcast_batting_test(previous)
        elif choice == "7":
            previous = run_pitch_performance_test(previous)
        elif choice == "8":
            previous = run_division_standings_test(previous)
        elif choice == "9":
            previous = run_wildcard_standings_test(previous)
        elif choice == "10":
            previous = run_sting_test(previous)

        # SLEEP_BETWEEN_PUSHES: comment out to remove the pause
        time.sleep(5)


if __name__ == "__main__":
    main()
