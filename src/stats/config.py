
##this is twofold
##1) determining which stats need to be ordered in which direction based on hitting and pitching (ERA, for example. Lower is better.)
##2) all stats here are on the list of stats that can be randomly called in main.py for rendering the leaderboards

STAT_CONFIG = {
    "avg":                  {"ascending": False, "type": "hitting",  "agg": "rate", "label": "AVG", "active": True, "team_leaderboard_active": True},
    "ops":                  {"ascending": False, "type": "hitting",  "agg": "rate", "label": "OPS", "active": True, "team_leaderboard_active": True},
    "obp":                  {"ascending": False, "type": "hitting",  "agg": "rate", "label": "OBP", "active": True, "team_leaderboard_active": True},
    "slg":                  {"ascending": False, "type": "hitting",  "agg": "rate", "label": "Slugging %", "active": True, "team_leaderboard_active": True},
    "homeRuns":             {"ascending": False, "type": "hitting",  "agg": "sum",  "label": "HR", "active": True, "team_leaderboard_active": True},
    "runs":                 {"ascending": False, "type": "hitting",  "agg": "sum",  "label": "Runs", "active": True, "team_leaderboard_active": True},
    "doubles":              {"ascending": False, "type": "hitting",  "agg": "sum",  "label": "Doubles", "active": True, "team_leaderboard_active": True},
    "triples":              {"ascending": False, "type": "hitting",  "agg": "sum",  "label": "Triples", "active": True, "team_leaderboard_active": True},
    "hits":                 {"ascending": False, "type": "hitting",  "agg": "sum",  "label": "Hits", "active": True, "team_leaderboard_active": True},
    "rbi":                  {"ascending": False, "type": "hitting",  "agg": "sum",  "label": "RBI", "active": True, "team_leaderboard_active": True},
    "stolenBases":          {"ascending": False, "type": "hitting",  "agg": "sum",  "label": "Stolen Bases", "active": True, "team_leaderboard_active": True},
    "baseOnBalls":          {"ascending": False, "type": "hitting",  "agg": "sum",  "label": "Base on Balls", "active": True, "team_leaderboard_active": True},
    "plateAppearances":     {"ascending": False, "type": "hitting",  "agg": "sum",  "label": "Plate Appearances", "active": True, "team_leaderboard_active": True},
    "babip":                {"ascending": False, "type": "hitting",  "agg": "rate", "label": "BABIP", "active": True, "team_leaderboard_active": True},
    "strikeOuts":           {"ascending": False,  "type": "hitting",  "agg": "sum",  "label": "Strikeouts", "active": True, "team_leaderboard_active": True},
    "groundIntoDoublePlay": {"ascending": False, "type": "hitting",  "agg": "sum",  "label": "GIDP", "active": True, "team_leaderboard_active": True},
    "xba":                   {"ascending": False, "type": "hitting",  "agg": "rate", "label": "xBA", "active": False, "team_leaderboard_active": False},
    "slg":                   {"ascending": False, "type": "hitting",  "agg": "rate", "label": "SLG", "active": False, "team_leaderboard_active": False},
    'xslg':                  {"ascending": False, "type": "hitting",  "agg": "rate", "label": "xSLG", "active": False, "team_leaderboard_active": False},
    "woba":                  {"ascending": False, "type": "hitting",  "agg": "rate", "label": "wOBA", "active": False, "team_leaderboard_active": False},
    'xwoba':                 {"ascending": False, "type": "hitting",  "agg": "rate", "label": "xwOBA", "active": False, "team_leaderboard_active": False},
    'exit_velocity':         {"ascending": False, "type": "hitting",  "agg": "rate", "label": "AVG. EV", "active": False, "team_leaderboard_active": False},
    'barrel_rate':          {"ascending": False, "type": "hitting",  "agg": "rate", "label": "BARREL %", "active": False, "team_leaderboard_active": False},
    'avg_distance':         {"ascending": False, "type": "hitting",  "agg": "rate", "label": "AVG. DIST", "active": False, "team_leaderboard_active": False},
    'slg_diff': {"ascending": False, "type": "hitting",  "agg": "rate", "label": "xSLG ADJUSTMENT", "active": False, "team_leaderboard_active": False},
    'avg_bat_speed':         {"ascending": False, "type": "hitting",  "agg": "rate", "label": "BAT SPEED", "active": False, "team_leaderboard_active": False},
    'whiff_percent':         {"ascending": True, "type": "hitting",  "agg": "rate", "label": "WHIFF %", "active": False, "team_leaderboard_active": False},


    "era":                  {"ascending": True,  "type": "pitching", "agg": "rate", "label": "ERA", "active": True, "team_leaderboard_active": True},
    "whip":                 {"ascending": True,  "type": "pitching", "agg": "rate", "label": "WHIP", "active": True, "team_leaderboard_active": True},
    "wins":                 {"ascending": False, "type": "pitching", "agg": "sum",  "label": "Wins", "active": True, "team_leaderboard_active": True},
    "saves":                {"ascending": False, "type": "pitching", "agg": "sum",  "label": "Saves", "active": True, "team_leaderboard_active": True},
    "pitchingStrikeOuts":   {"ascending": False, "type": "pitching", "agg": "sum",  "label": "SO", "active": True, "team_leaderboard_active": True},
    "strikeoutsPer9Inn":    {"ascending": False, "type": "pitching", "agg": "rate", "label": "K/9", "active": True, "team_leaderboard_active": True},
    "inningsPitched":       {"ascending": False, "type": "pitching", "agg": "sum",  "label": "IP", "active": True, "team_leaderboard_active": True},
    "gamesPitched":         {"ascending": False, "type": "pitching", "agg": "sum",  "label": "Appearances", "active": True, "team_leaderboard_active": True},
    "gamesStarted":         {"ascending": False, "type": "pitching", "agg": "sum",  "label": "Games Started", "active": False, "team_leaderboard_active": False},
    "strikePercentage":     {"ascending": False, "type": "pitching", "agg": "rate", "label": "Strike %", "active": True, "team_leaderboard_active": True},
    "walksPer9Inn":         {"ascending": True,  "type": "pitching", "agg": "rate", "label": "BB/9", "active": True, "team_leaderboard_active": False},
    "hitsPer9Inn":          {"ascending": True,  "type": "pitching", "agg": "rate", "label": "H/9", "active": True, "team_leaderboard_active": False},
    "homeRunsPer9":         {"ascending": True,  "type": "pitching", "agg": "rate", "label": "HR/9", "active": True, "team_leaderboard_active": False},
    "losses":               {"ascending": True,  "type": "pitching", "agg": "sum",  "label": "Losses", "active": True, "team_leaderboard_active": False},
    "blownSaves":           {"ascending": False, "type": "pitching", "agg": "sum",  "label": "Blown Saves", "active": False, "team_leaderboard_active": True},
    "earnedRuns":           {"ascending": False, "type": "pitching", "agg": "sum",  "label": "Earned Runs ", "active": True, "team_leaderboard_active": True},
    "xera":                 {"ascending": True,  "type": "pitching", "agg": "rate", "label": "xERA", "active": False, "team_leaderboard_active": False},
    "woba_against":                  {"ascending": True, "type": "pitching",  "agg": "rate", "label": "wOBA", "active": False, "team_leaderboard_active": False},
    'xwoba_against':                 {"ascending": True, "type": "pitching",  "agg": "rate", "label": "xwOBA", "active": False, "team_leaderboard_active": False},
    'xba_against':                   {"ascending": True, "type": "pitching",  "agg": "rate", "label": "xBA AGAINST", "active": False, "team_leaderboard_active": False},
    'babip_against':                 {"ascending": True, "type": "pitching",  "agg": "rate", "label": "BABIP", "active": False, "team_leaderboard_active": False},
    'xslg_against':                  {"ascending": True, "type": "pitching",  "agg": "rate", "label": "xSLG", "active": False, "team_leaderboard_active": False},
    'slg_against':                   {"ascending": True, "type": "pitching",  "agg": "rate", "label": "SLG", "active": False, "team_leaderboard_active": False},
    'exit_velocity_against':         {"ascending": True, "type": "pitching",  "agg": "rate", "label": "AVG. EV", "active": False, "team_leaderboard_active": False},
    'barrel_rate_against':          {"ascending": True, "type": "pitching",  "agg": "rate", "label": "BARREL %", "active": False, "team_leaderboard_active": False},
    'avg_distance':         {"ascending": False, "type": "pitching",  "agg": "rate", "label": "AVG. DIST", "active": False, "team_leaderboard_active": False},
    'era_diff': {"ascending": False, "type": "pitching",  "agg": "rate", "label": "xERA ADJUSTMENT", "active": False, "team_leaderboard_active": False},
    'ba':                   {"ascending": True,  "type": "pitching",  "agg": "rate", "label": "BA", "active": False, "team_leaderboard_active": False},
    'hard_hit_percent':     {"ascending": True,  "type": "pitching",  "agg": "rate", "label": "Hard Hit %", "active": False, "team_leaderboard_active": False},
    'whiff_percent_against':        {"ascending": False, "type": "pitching",  "agg": "rate", "label": "WHIFF %", "active": False, "team_leaderboard_active": False},
    'fastball_velo':        {"ascending": False, "type": "pitching",  "agg": "rate", "label": "FB. VELO", "active": False, "team_leaderboard_active": True},
}

HISTORY_CONFIG = {
    "seasons": 5,
    "stats": {
        "team": {"type": "both", "label": "TEAM", "active": True},
        "gamesPlayed": {"type": "hitting", "label": "G", "active": True},
        "atBats": {"type": "hitting", "label": "AB", "active": True},
        "hits": {"type": "hitting", "label": "H", "active": True},
        "homeRuns": {"type": "hitting", "label": "HR", "active": False},
        "runs": {"type": "hitting", "label": "R", "active": False},
        "ops": {"type": "hitting", "label": "OPS", "active": True},
        "rbi": {"type": "hitting", "label": "RBI", "active": False},
        "baseOnBalls": {"type": "both", "label": "BB", "active": False},
        "stolenBases": {"type": "hitting", "label": "SB", "active": False},
        "gamesPitched": {"type": "pitching", "label": "GP ", "active": True},
        "wins": {"type": "pitching", "label": "W", "active": False},
        "losses": {"type": "pitching", "label": "L", "active": False},
        "inningsPitched": {"type": "pitching", "label": "IP", "active": True},
        "pitchingStrikeOuts": {"type": "pitching", "label": "K", "active": True},
        "era": {"type": "pitching", "label": "ERA", "active": True},
    }
}

##controls both the row count and which stat columns show up for the
##recent-appearances (per-game) table. add/remove a stat by adding a line
##or flipping "active"; change how many games are shown by editing "games".
##"order" controls left-to-right column position (lower = further left) —
##change the number to reorder without moving lines around.
RECENT_APPEARANCES_CONFIG = {
    "games": 6,
    "stats": {
        "atBats":         {"type": "hitting",  "label": "AB",  "active": True, "order": 1},
        "hits":           {"type": "both",     "label": "H",   "active": True, "order": 2},
        "totalBases":     {"type": "hitting",  "label": "TB",  "active": True, "order": 3},
        "rbi":            {"type": "hitting",  "label": "RBI", "active": True, "order": 4},
        "strikeOuts":     {"type": "both",     "label": "K",   "active": True, "order": 5},
        "baseOnBalls":    {"type": "both",     "label": "BB",  "active": True, "order": 6},
        "inningsPitched": {"type": "pitching", "label": "IP",  "active": True, "order": 1},
        "earnedRuns":     {"type": "pitching", "label": "ER",  "active": True, "order": 2},
        "runs":           {"type": "pitching", "label": "R",   "active": True, "order": 3},
    },
}

