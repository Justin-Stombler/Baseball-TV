import random
import time
import re

from data.team_abbreviations import TEAM_ABBREVIATIONS
from src.config import DISPLAY_CONFIG
from src.push import push, delete
from src.render.leaderboard import render_leaderboard
from src.render.player_profiles import render_player_profiles
from src.render.player_stats import render_player_stats
from src.render.batted_ball_profile import render_batted_ball_profile
from src.render.statcast_expected import render_statcast_data
from src.render.stings import render_sting, stings
from src.render.team_leaderboard import render_team_leaderboard
from src.render.team_profile import render_team_profile
from src.render.pitch_arsenal import render_pitch_arsenal
from src.render.division_standings import render_division_standings
from src.render.wildcard_standings import render_wildcard_standings
from src.render.box_score import render_division_box_scores
from src.render.recent_appearances import render_recent_appearances
from src.stats.config import STAT_CONFIG
from src.transforms.leaderboard import generate_leaderboard
from src.transforms.player_bios import bio_list
from src.transforms.player_history import player_history
from src.transforms.player_stats import player_list
from src.transforms.batted_ball_profile import player_list as batted_ball_player_list
from src.transforms.statcast_expected import expected_stats_list
from src.transforms.team_leaderboard import generate_team_leaderboard, get_available_teams
from src.transforms.team_profiles import generate_team_profile
from src.transforms.pitch_arsenal import generate_pitch_arsenal
from src.transforms.standings import generate_division_standings, generate_wild_card_standings
from src.transforms.box_score import generate_division_box_scores

# lowercase abbreviation (e.g. "bos") -> full team name (e.g. "Boston Red Sox")
TEAM_BY_ABBREVIATION = {abbr.lower(): name for name, abbr in TEAM_ABBREVIATIONS.items()}


def display(image: bytes, duration: int, previous: str | None, filename: str | None = None) -> str:
    """Push image, delete previous, wait duration. Returns current filename."""
    current = push(image, filename=filename)
    if previous:
        delete(previous)
    time.sleep(duration)
    return current


def filter_players(players: list[dict], group: str | None = None, team: str | None = None) -> list[dict]:
    """Narrow a player list down to one group (hitter/pitcher) and/or one team.

    `group` matches the position in ('SP', 'RP') convention used across transforms.
    `team` matches the full team name stored on player['team'].
    """
    if group == "pitcher":
        players = [p for p in players if p.get("position") in ("SP", "RP")]
    elif group == "hitter":
        players = [p for p in players if p.get("position") not in ("SP", "RP")]

    if team:
        players = [p for p in players if p.get("team") == team]

    return players


# Shared "anchor" player for the player-card modes (2-5). run_player_stats_test sets
# it fresh each time it runs; the other three modes reuse it if their dataset has a
# matching player, so selecting e.g. "2 3 4 5" rotates through one player's cards
# instead of picking a new random player for each mode.
_rotation_player: dict | None = None


def run_player_stats_test(previous: str | None, group: str | None = None, team: str | None = None) -> str:
    global _rotation_player
    cfg = DISPLAY_CONFIG["player_stats"]
    players = filter_players(player_list(), group, team)
    if not players:
        print(f"No player_stats players available for group '{group}', team '{team}'. Try again.")
        return previous
    player = random.choice(players)
    _rotation_player = player
    current = display(render_player_stats(player), cfg["duration"], previous=previous)
    print("Pushed mode: player_stats")
    return current


def run_statcast_expected_test(previous: str | None, group: str | None = None, team: str | None = None) -> str:
    cfg = DISPLAY_CONFIG["statcast_expected"]
    players = filter_players(expected_stats_list(), group, team)
    if not players:
        print(f"No statcast_expected players available for group '{group}', team '{team}'. Try again.")
        return previous

    if _rotation_player:
        player = {p["id"]: p for p in players}.get(_rotation_player["id"])
        if not player:
            print(f"[statcast_expected] No data for rotation player {_rotation_player.get('name')} (id={_rotation_player.get('id')}). Skipping, keeping previous image.")
            return previous
    else:
        player = random.choice(players)

    current = display(render_statcast_data(player), cfg["duration"], previous=previous)
    print("Pushed mode: statcast_expected")
    return current


def run_batted_ball_profile_test(previous: str | None, group: str | None = None, team: str | None = None) -> str:
    cfg = DISPLAY_CONFIG["batted_ball_profile"]
    players = filter_players(batted_ball_player_list(), group, team)
    if not players:
        print(f"No batted_ball_profile players available for group '{group}', team '{team}'. Try again.")
        return previous

    if _rotation_player:
        player = {p["id"]: p for p in players}.get(_rotation_player["id"])
        if not player:
            print(f"[batted_ball_profile] No data for rotation player {_rotation_player.get('name')} (id={_rotation_player.get('id')}). Skipping, keeping previous image.")
            return previous
    else:
        player = random.choice(players)

    current = display(render_batted_ball_profile(player), cfg["duration"], previous=previous)
    print("Pushed mode: batted_ball_profile")
    return current


def run_player_profiles_test(previous: str | None, group: str | None = None, team: str | None = None) -> str | None:
    cfg = DISPLAY_CONFIG["player_profiles"]
    history_count = cfg.get("seasons")

    players = filter_players(player_list(), group, team)
    if not players:
        print(f"No player_profiles players available for group '{group}', team '{team}'. Try again.")
        return previous

    bio_by_id = {b["id"]: b for b in bio_list()}
    bio = None
    player = None

    if _rotation_player:
        bio = bio_by_id.get(_rotation_player["id"])
        player = _rotation_player
        if not bio:
            print(f"[player_profiles] No bio for rotation player {_rotation_player.get('name')} (id={_rotation_player.get('id')}). Skipping, keeping previous image.")
            return previous
    else:
        # No anchor set (e.g. mode 5 run on its own); try candidates in random order until one hits.
        random.shuffle(players)
        for candidate in players:
            bio = bio_by_id.get(candidate["id"])
            if bio:
                player = candidate
                break

    if not bio:
        print(f"No matching bio found for group '{group}', team '{team}'. Try again.")
        return previous

    history_dict = player_history([bio], count=history_count)
    bio = {**bio, "history": history_dict.get(player["id"], [])}
    current = display(render_player_profiles(bio), cfg["duration"], previous=previous)
    print("Pushed mode: player_profiles")
    return current


def run_recent_appearances_test(previous: str | None, group: str | None = None, team: str | None = None) -> str | None:
    cfg = DISPLAY_CONFIG["recent_appearances"]
    players = filter_players(player_list(), group, team)
    if not players:
        print(f"No recent_appearances players available for group '{group}', team '{team}'. Try again.")
        return previous

    bio_by_id = {b["id"]: b for b in bio_list()}
    bio = None
    player = None

    if _rotation_player:
        bio = bio_by_id.get(_rotation_player["id"])
        player = _rotation_player
        if not bio:
            print(f"[recent_appearances] No bio for rotation player {_rotation_player.get('name')} (id={_rotation_player.get('id')}). Skipping, keeping previous image.")
            return previous
    else:
        random.shuffle(players)
        for candidate in players:
            bio = bio_by_id.get(candidate["id"])
            if bio:
                player = candidate
                break

    if not bio:
        print(f"No matching bio found for group '{group}', team '{team}'. Try again.")
        return previous

    current = display(render_recent_appearances(bio), cfg["duration"], previous=previous)
    print("Pushed mode: recent_appearances")
    return current


def run_leaderboard_test(previous: str | None, group: str | None = None, team: str | None = None) -> str:
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

def run_team_leaderboard_test(previous: str | None, group: str | None = None, team: str | None = None) -> str:
    cfg = DISPLAY_CONFIG["team_leaderboard"]
    active_stats = [k for k, v in STAT_CONFIG.items() if v.get("team_leaderboard_active", True)]
    stat = random.choice(active_stats)
    teams = get_available_teams(stat=stat)
    if not teams:
        raise RuntimeError(f"No teams available for stat '{stat}'.")
    selected_team = team if team in teams else random.choice(teams)

    leaderboard = generate_team_leaderboard(team=selected_team, stat=stat)
    current = display(
        render_team_leaderboard(leaderboard, stat=stat, team=selected_team),
        cfg["duration"],
        previous=previous,
        filename=f"team__{stat}.jpg",
    )
    print(f"Pushed mode: team_leaderboard ({selected_team}, {stat})")
    return current

def run_team_profile_test(previous: str | None, group: str | None = None, team: str | None = None) -> str:
    cfg = DISPLAY_CONFIG["team_profiles"]
    profiles = generate_team_profile()
    if team:
        matching = [p for p in profiles if p.get("team_name") == team]
        profiles = matching or profiles
    selected = random.choice(profiles)
    current = display(render_team_profile(selected), cfg["duration"], previous=previous)
    print("Pushed mode: team_profile")
    return current

def run_sting_test(previous: str | None, group: str | None = None, team: str | None = None) -> str:
    cfg = DISPLAY_CONFIG["stings"]
    sting_text = random.choice(stings)
    current = display(render_sting(sting_text), cfg["duration"], previous=previous)
    print("Pushed mode: stings")
    return current

def run_division_standings_test(previous: str | None, group: str | None = None, team: str | None = None) -> str:
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


def run_wildcard_standings_test(previous: str | None, group: str | None = None, team: str | None = None) -> str:
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


# Cycles through all 6 divisions (AL/NL x East/Central/West) one call at a time.
_BOX_SCORE_DIVISIONS = [(league, division) for league in ("AL", "NL") for division in ("East", "Central", "West")]


def run_box_score_test(previous: str | None, group: str | None = None, team: str | None = None) -> str:
    cfg = DISPLAY_CONFIG["box_score"]
    index = getattr(run_box_score_test, "_next_index", 0)
    league, division = _BOX_SCORE_DIVISIONS[index]

    games = generate_division_box_scores(league=league, division=division)
    current = display(
        render_division_box_scores(games, division=division, league=league),
        cfg["duration"],
        previous=previous,
    )

    run_box_score_test._next_index = (index + 1) % len(_BOX_SCORE_DIVISIONS)
    print(f"Pushed mode: box_score ({league} {division})")
    return current

def run_pitch_arsenal_test(previous: str | None, group: str | None = None, team: str | None = None) -> str:
    cfg = DISPLAY_CONFIG["pitch_arsenal"]

    if group == "hitter":
        print("pitch_arsenal is pitcher-only; ignoring hitter group filter.")

    pitchers = filter_players(generate_pitch_arsenal(qualified_only=True), group="pitcher", team=team)
    if not pitchers:
        print(f"No pitch arsenal pitcher data available for team '{team}'. Try again.")
        return previous

    player = random.choice(pitchers)
    detailed = generate_pitch_arsenal(
        player_id=player["player_id"],
        qualified_only=True,
        include_movement=True,
    )
    if detailed:
        player = detailed[0]

    current = display(render_pitch_arsenal(player), cfg["duration"], previous=previous)
    print("Pushed mode: pitch_arsenal (pitcher)")
    return current

MODE_DISPATCH = {
    "1": ("stings", run_sting_test),
    "2": ("player_stats", run_player_stats_test),
    "3": ("statcast_expected", run_statcast_expected_test),
    "4": ("batted_ball_profile", run_batted_ball_profile_test),
    "5": ("player_profiles", run_player_profiles_test),
    "6": ("leaderboard", run_leaderboard_test),
    "7": ("team_leaderboard", run_team_leaderboard_test),
    "8": ("division_standings", run_division_standings_test),
    "9": ("wildcard_standings", run_wildcard_standings_test),
    "10": ("team_profiles", run_team_profile_test),
    "11": ("pitch_arsenal", run_pitch_arsenal_test),
    "12": ("box_score", run_box_score_test),
    "13": ("recent_appearances", run_recent_appearances_test),
}


def choose_modes_group_team() -> tuple[list[str], str | None, str | None]:
    while True:
        print("Choose one or more modes to test push output, in carousel order:")
        for key, (name, _) in MODE_DISPATCH.items():
            print(f"{key}) {name}")
        print("Optionally follow with a group (b=batters, p=pitchers) and/or a team abbreviation (e.g. bos, nyy).")
        print("Modes 2-5 and 13 will attempt to use the same player when called and log if not possible")
        raw_choice = input("Enter modes [group] [team] (e.g. '2, 3, 4, 5 b bos'): ").strip()

        # Split on any mix of commas and/or whitespace between tokens.
        tokens = [t for t in re.split(r"[\s,]+", raw_choice) if t]
        if not tokens:
            print("Invalid choice(s). Please enter valid values.")
            continue

        mode_tokens = [t for t in tokens if t in MODE_DISPATCH]
        remainder = [t for t in tokens if t not in MODE_DISPATCH]

        if not mode_tokens:
            print("Invalid choice(s). Please enter valid values.")
            continue

        group: str | None = None
        team: str | None = None
        valid = True
        for token in remainder:
            lowered = token.lower()
            if lowered in {"b", "batter", "batters", "h", "hitter", "hitters"}:
                group = "hitter"
            elif lowered in {"p", "pitcher", "pitchers"}:
                group = "pitcher"
            elif lowered in TEAM_BY_ABBREVIATION:
                team = TEAM_BY_ABBREVIATION[lowered]
            else:
                print(f"Unrecognized group/team value: '{token}'.")
                valid = False
                break

        if valid:
            return mode_tokens, group, team


def main() -> None:
    modes, group, team = choose_modes_group_team()
    previous = None

    index = 0
    while True:
        choice = modes[index % len(modes)]
        _, run_fn = MODE_DISPATCH[choice]
        previous = run_fn(previous, group, team)
        index += 1

        # SLEEP_BETWEEN_PUSHES: comment out to remove the pause
        time.sleep(5)


if __name__ == "__main__":
    main()
