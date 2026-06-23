
##this is twofold
##1) determining which stats need to be ordered in which direction based on hitting and pitching (ERA, for example. Lower is better.)
##2) all stats here are on the list of stats that can be randomly called in main.py for rendering the leaderboards

DISPLAY_CONFIG = {
    "startup": {"duration": 5},
    "player_stats": {"duration": 5, "count": 3},
    "statcast_batting": {"duration": 5, "count": 3},
    "player_profiles": {"duration": 7, "count": 3, "seasons": 5},
    "leaderboard":  {"duration": 5, "count": 3, "leagues": ["AL", "NL"]},
    "team_leaderboard": {"duration": 5, "count": 1, "stat_count": 2, "team_count": 3, "min_ab": 20, "min_ip": 10},
    "batted_ball_profile": {"duration": 5, "count": 3},
    "pitch_performance": {"duration": 5, "count": 3},
    "division_standings": {"duration": 5, "count": 3},
    "stings": {"duration": 5, "count": 1},
}