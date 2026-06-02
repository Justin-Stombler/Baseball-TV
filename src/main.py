from .transforms.player_stats import player_list
from .transforms.player_bios import bio_list
from .transforms.player_history import player_history
from .transforms.leaderboard import generate_leaderboard
from .render.player_stats import render_player_stats
from .render.player_profiles import render_player_profiles
from .render.leaderboard import render_leaderboard
from .push import push, delete
from .config import DISPLAY_CONFIG
from .stats.config import STAT_CONFIG
import random
import time

def display(image: bytes, duration: int, previous: str | None, filename: str = None) -> str:
    """Push image, delete previous, wait duration. Returns current filename."""
    current = push(image, filename=filename)
    if previous:
        delete(previous)
    time.sleep(duration)
    return current

if __name__ == "__main__":
    ps = DISPLAY_CONFIG["player_stats"]
    pp = DISPLAY_CONFIG["player_profiles"]
    history_count = pp.get("seasons")
    lb = DISPLAY_CONFIG["leaderboard"]
    previous = None

    while True:
        ##Load players and bios fresh for each cycle
        players = player_list()
        bios = bio_list()
        bio_by_id = {b['id']: b for b in bios}
        
        ##show stat card then profile card for each player
        for _ in range(ps["count"]):
            player = random.choice(players)
            previous = display(render_player_stats(player), ps["duration"], previous)
            
            bio = bio_by_id.get(player['id'])
            if bio:
                # Generate history just-in-time for this one profile
                history_dict = player_history([bio], count=history_count)
                bio = {**bio, 'history': history_dict.get(player['id'], [])}
                try:
                    profile_bytes = render_player_profiles(bio)
                    previous = display(profile_bytes, pp["duration"], previous)
                except Exception as e:
                    print(f"Error rendering profile for {bio.get('name')}: {e}")

        for _ in range(lb["count"]):
            active_stats = [k for k, v in STAT_CONFIG.items() if v.get("active", True)]
            stat = random.choice(active_stats)
            for league in lb["leagues"]:
                leaderboard = generate_leaderboard(league=league, stat=stat)
                previous = display(render_leaderboard(leaderboard, stat=stat, league=league), lb["duration"], previous, filename=f"{stat}_{league}.jpg")