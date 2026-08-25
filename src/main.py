from .transforms.player_stats import player_list
from .transforms.player_bios import bio_list
from .transforms.player_history import player_history
from .transforms.leaderboard import generate_leaderboard
from .transforms.batted_ball_profile import player_list as batted_ball_player_list
from .transforms.statcast_batting import expected_stats_list
from .transforms.team_leaderboard import generate_team_leaderboard, get_available_teams
from .transforms.team_profiles import generate_team_profile
from .transforms.standings import generate_division_standings, generate_wild_card_standings
from .transforms.box_score import generate_division_box_scores
from .transforms.pitch_arsenal import generate_pitch_arsenal
from .render.player_stats import render_player_stats
from .render.player_profiles import render_player_profiles
from .render.leaderboard import render_leaderboard
from .render.batted_ball_profile import render_batted_ball_profile
from .render.statcast_batting import render_statcast_data
from .render.startup import render_startup
from .render.stings import render_sting, stings
from .render.team_leaderboard import render_team_leaderboard
from .render.expanded_team_profile import render_expanded_team_profile
from .render.division_standings import render_division_standings
from .render.wildcard_standings import render_wildcard_standings
from .render.box_score import render_division_box_scores
from .render.pitch_arsenal import render_pitch_arsenal
from .push import push, delete
from .config import DISPLAY_CONFIG
from .stats.config import STAT_CONFIG
from .constants import DATA_DIR
import random
import time
import json
import subprocess
import os

_last_display_at: float | None = None

def display(image: bytes, duration: int, previous: str | None, filename: str = None, mode: str = "unknown") -> str:
    """Push image, delete previous, wait duration. Returns current filename."""
    global _last_display_at

    current = push(image, filename=filename)

    if previous:
        delete(previous)

    _last_display_at = time.time()
    time.sleep(duration)
    return current


def startup_sequence(startup_cfg: dict) -> str | None:
    """Display startup screen and fetch fresh roster data. Move to next display immediately after fetch completes."""
    startup_bytes = render_startup()
    previous = push(startup_bytes, filename="startup.jpg")
    
    try:
        print("Fetching all MLB rosters...")
        # Run fetch_roster.py directly via subprocess
        script_path = os.path.join(os.path.dirname(__file__), '..', 'setup_files', 'fetch_roster.py')
        result = subprocess.run(
            ['python', script_path],
            capture_output=True,
            text=True,
            cwd=os.path.join(os.path.dirname(__file__), '..')
        )
        print(result.stdout)
        if result.returncode != 0:
            print(f"Warning: fetch_roster returned error: {result.stderr}")
    except Exception as e:
        print(f"Error during startup: {e}")
    
    # Return immediately - move to next display as soon as fetch is done
    return previous


if __name__ == "__main__":

    ps = DISPLAY_CONFIG["player_stats"]
    pp = DISPLAY_CONFIG["player_profiles"]
    history_count = pp.get("seasons")
    lb = DISPLAY_CONFIG["leaderboard"]
    tlb = DISPLAY_CONFIG["team_leaderboard"]
    bbp = DISPLAY_CONFIG["batted_ball_profile"]
    sb = DISPLAY_CONFIG["statcast_batting"]
    ds = DISPLAY_CONFIG["division_standings"]
    ws = DISPLAY_CONFIG["wildcard_standings"]
    bs = DISPLAY_CONFIG["box_score"]
    tp = DISPLAY_CONFIG["team_profiles"]
    pa = DISPLAY_CONFIG["pitch_arsenal"]
    stings_cfg = DISPLAY_CONFIG["stings"]
    startup_cfg = DISPLAY_CONFIG["startup"]
    
    # Standings cycle: 0=AL divisions, 1=NL divisions, 2=wildcard
    standings_cycle = 0
    # Box score cycle: 0=AL, 1=NL (independent of standings_cycle, so it'll drift out of sync)
    box_score_cycle = 0

    ##if command included --hot 
    if "--hot" in os.sys.argv:
        print("Hot mode enabled: skipping startup sequence and using last display as previous.")
        previous = None
        if os.path.exists(os.path.join(DATA_DIR, "last_display.json")):
            with open(os.path.join(DATA_DIR, "last_display.json"), "r") as f:
                last_display_data = json.load(f)
                previous = last_display_data.get("last_display")
                print(f"Using last display: {previous}")
    else:
        previous = startup_sequence(startup_cfg)

    while True:
        ##Load players and bios fresh for each cycle
        players = player_list()
        bios = bio_list()
        batted_ball_profiles = batted_ball_player_list()
        bio_by_id = {b['id']: b for b in bios}
        is_pitcher = lambda player: player.get('position') in ['P', 'SP', 'RP', 'TWP']

        for _ in range(stings_cfg["count"]):
            sting_text = random.choice(stings)
            previous = display(render_sting(sting_text), stings_cfg["duration"], previous=previous, mode="stings")
            print("Pushed mode: stings")
        
        ##show stat card then profile card for each player
        for _ in range(ps["count"]):
            player = random.choice(players)
            previous = display(render_player_stats(player), ps["duration"], previous, mode="player_stats")

            ##show statcast batting profile for the player used above
            statcast_batting_players_by_id = {p['id']: p for p in expected_stats_list()}
            sb_player = statcast_batting_players_by_id.get(player['id'])
            if sb_player:
                try:
                    sb_bytes = render_statcast_data(sb_player)
                    previous = display(sb_bytes, sb["duration"], previous, mode="statcast_batting")
                except Exception as e:
                    print(f"Error rendering statcast data for {sb_player.get('name')}: {e}")

            ##i want to sohw the batted ball profile for the player used above
            batted_ball_players_by_id = {p['id']: p for p in batted_ball_profiles}
            bbp_player = batted_ball_players_by_id.get(player['id'])
            if bbp_player:
                try:
                    bbp_bytes = render_batted_ball_profile(bbp_player)
                    previous = display(bbp_bytes, bbp["duration"], previous, mode="batted_ball_profile")
                except Exception as e:
                    print(f"Error rendering batted ball profile for {bbp_player.get('name')}: {e}")

            ##if player is pitcher then also run pitch arsenal for the player used above
            if is_pitcher(player):
                player_data = generate_pitch_arsenal(player_id=player["id"], qualified_only=False, include_movement=True)
                pa_bytes = render_pitch_arsenal(player_data[0])
                previous = display(pa_bytes, pa["duration"], previous, mode="pitch_arsenal")


            bio = bio_by_id.get(player['id'])
            if bio:
                # Generate history just-in-time for this one profile
                history_dict = player_history([bio], count=history_count)
                bio = {**bio, 'history': history_dict.get(player['id'], [])}
                try:
                    profile_bytes = render_player_profiles(bio)
                    previous = display(profile_bytes, pp["duration"], previous, mode="player_profiles")
                except Exception as e:
                    print(f"Error rendering profile for {bio.get('name')}: {e}")

        for _ in range(stings_cfg["count"]):
            sting_text = random.choice(stings)
            previous = display(render_sting(sting_text), stings_cfg["duration"], previous=previous, mode="stings")
            print("Pushed mode: stings")

        for _ in range(lb["count"]):
            active_stats = [k for k, v in STAT_CONFIG.items() if v.get("active", True)]
            stat = random.choice(active_stats)
            for league in lb["leagues"]:
                leaderboard = generate_leaderboard(league=league, stat=stat)
                previous = display(render_leaderboard(leaderboard, stat=stat, league=league), lb["duration"], previous, filename=f"{stat}_{league}.jpg", mode="leaderboard")

        for _ in range(stings_cfg["count"]):
            sting_text = random.choice(stings)
            previous = display(render_sting(sting_text), stings_cfg["duration"], previous=previous, mode="stings")
            print("Pushed mode: stings")

        for _ in range(tlb["count"]):
            active_stats = [k for k, v in STAT_CONFIG.items() if v.get("team_leaderboard_active", True)]
            selected_stats = random.sample(active_stats, min(tlb["stat_count"], len(active_stats)))
            for stat in selected_stats:
                available_teams = get_available_teams(stat=stat, qualified_only=False)
                selected_teams = random.sample(available_teams, min(tlb["team_count"], len(available_teams)))
                for team in selected_teams:
                    stat_type = STAT_CONFIG.get(stat, {}).get('type')
                    min_ab = tlb.get("min_ab") if stat_type == 'hitting' else 0
                    min_ip = tlb.get("min_ip") if stat_type == 'pitching' else 0.0
                    team_leaderboard = generate_team_leaderboard(team=team, stat=stat, qualified_only=False, min_ab=min_ab, min_ip=min_ip)
                    previous = display(render_team_leaderboard(team_leaderboard, stat=stat, team=team), tlb["duration"], previous, mode="team_leaderboard")

        for _ in range(stings_cfg["count"]):
            sting_text = random.choice(stings)
            previous = display(render_sting(sting_text), stings_cfg["duration"], previous=previous, mode="stings")
            print("Pushed mode: stings")

        # 3-cycle standings rotation: 0=AL div, 1=NL div, 2=wildcard
        if standings_cycle == 0:
            # AL division standings: East, Central, West
            divisions = ["East", "Central", "West"]
            for division in divisions:
                standings = generate_division_standings(league="AL", division=division)
                previous = display(render_division_standings(standings=standings, division=division, league="AL"), ds["duration"], previous, mode="division_standings_AL")
            print("Pushed mode: division_standings (AL East/Central/West)")
        elif standings_cycle == 1:
            # NL division standings: East, Central, West
            divisions = ["East", "Central", "West"]
            for division in divisions:
                standings = generate_division_standings(league="NL", division=division)
                previous = display(render_division_standings(standings=standings, division=division, league="NL"), ds["duration"], previous, mode="division_standings_NL")
            print("Pushed mode: division_standings (NL East/Central/West)")
        else:
            # Wildcard standings: AL and NL
            for league in ["AL", "NL"]:
                standings = generate_wild_card_standings(league=league)
                previous = display(render_wildcard_standings(standings=standings, league=league), ws["duration"], previous, mode="wildcard_standings")
            print("Pushed mode: wildcard_standings (AL, NL)")

        standings_cycle = (standings_cycle + 1) % 3
        
        # Box score: alternate AL, NL each pass through the loop; always shows East/Central/West
        box_score_league = "AL" if box_score_cycle == 0 else "NL"
        divisions = ["East", "Central", "West"]
        for division in divisions:
            games = generate_division_box_scores(league=box_score_league, division=division)
            previous = display(render_division_box_scores(games, division=division, league=box_score_league), bs["duration"], previous, mode=f"box_score_{box_score_league}")
        print(f"Pushed mode: box_score ({box_score_league} East/Central/West)")

        box_score_cycle = (box_score_cycle + 1) % 2

        for _ in range(stings_cfg["count"]):
            sting_text = random.choice(stings)
            previous = display(render_sting(sting_text), stings_cfg["duration"], previous=previous, mode="stings")
            print("Pushed mode: stings")

        profiles = generate_team_profile()
        if profiles:
            for _ in range(tp["count"]):
                team = random.choice(profiles)
                previous = display(render_expanded_team_profile(team), tp["duration"], previous, mode="team_profiles")
            print(f"Pushed mode: team_profiles ({tp['count']})")
        else:
            print("No team profile data available")
        
        
