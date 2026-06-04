
##this is twofold
##1) determining which stats need to be ordered in which direction based on hitting and pitching (ERA, for example. Lower is better.)
##2) all stats here are on the list of stats that can be randomly called in main.py for rendering the leaderboards

STAT_CONFIG = {
    "avg":                  {"ascending": False, "type": "hitting",  "agg": "rate", "label": "AVG", "active": True},
    "ops":                  {"ascending": False, "type": "hitting",  "agg": "rate", "label": "OPS", "active": True},
    "obp":                  {"ascending": False, "type": "hitting",  "agg": "rate", "label": "OBP", "active": True},
    "slg":                  {"ascending": False, "type": "hitting",  "agg": "rate", "label": "Slugging %", "active": True},
    "homeRuns":             {"ascending": False, "type": "hitting",  "agg": "sum",  "label": "HR", "active": True},
    "runs":                 {"ascending": False, "type": "hitting",  "agg": "sum",  "label": "Runs", "active": True},
    "doubles":              {"ascending": False, "type": "hitting",  "agg": "sum",  "label": "Doubles", "active": True},
    "triples":              {"ascending": False, "type": "hitting",  "agg": "sum",  "label": "Triples", "active": True},
    "hits":                 {"ascending": False, "type": "hitting",  "agg": "sum",  "label": "Hits", "active": True},
    "rbi":                  {"ascending": False, "type": "hitting",  "agg": "sum",  "label": "RBI", "active": True},
    "stolenBases":          {"ascending": False, "type": "hitting",  "agg": "sum",  "label": "Stolen Bases", "active": True},
    "baseOnBalls":          {"ascending": False, "type": "hitting",  "agg": "sum",  "label": "Base on Balls", "active": True},
    "plateAppearances":     {"ascending": False, "type": "hitting",  "agg": "sum",  "label": "Plate Appearances", "active": True},
    "babip":                {"ascending": False, "type": "hitting",  "agg": "rate", "label": "BABIP", "active": True},
    "strikeOuts":           {"ascending": True,  "type": "hitting",  "agg": "sum",  "label": "Strikeouts", "active": True},
    "groundIntoDoublePlay": {"ascending": False, "type": "hitting",  "agg": "sum",  "label": "GIDP", "active": True},

    "era":                  {"ascending": True,  "type": "pitching", "agg": "rate", "label": "ERA", "active": True},
    "whip":                 {"ascending": True,  "type": "pitching", "agg": "rate", "label": "WHIP", "active": True},
    "wins":                 {"ascending": False, "type": "pitching", "agg": "sum",  "label": "Wins", "active": True},
    "saves":                {"ascending": False, "type": "pitching", "agg": "sum",  "label": "Saves", "active": True},
    "pitchingStrikeOuts":   {"ascending": False, "type": "pitching", "agg": "sum",  "label": "SO", "active": True},
    "strikeoutsPer9Inn":    {"ascending": False, "type": "pitching", "agg": "rate", "label": "K/9", "active": True},
    "inningsPitched":       {"ascending": False, "type": "pitching", "agg": "sum",  "label": "IP", "active": True},
    "gamesPitched":         {"ascending": False, "type": "pitching", "agg": "sum",  "label": "Appearances", "active": True},
    "gamesStarted":         {"ascending": False, "type": "pitching", "agg": "sum",  "label": "Games Started", "active": False},
    "strikePercentage":     {"ascending": False, "type": "pitching", "agg": "rate", "label": "Strike %", "active": True},
    "walksPer9Inn":         {"ascending": True,  "type": "pitching", "agg": "rate", "label": "BB/9", "active": True},
    "hitsPer9Inn":          {"ascending": True,  "type": "pitching", "agg": "rate", "label": "H/9", "active": True},
    "homeRunsPer9":         {"ascending": True,  "type": "pitching", "agg": "rate", "label": "HR/9", "active": True},
    "losses":               {"ascending": True,  "type": "pitching", "agg": "sum",  "label": "Losses", "active": True},
    "blownSaves":           {"ascending": False, "type": "pitching", "agg": "sum",  "label": "Blown Saves", "active": False},
    "earnedRuns":           {"ascending": False, "type": "pitching", "agg": "sum",  "label": "Earned Runs ", "active": True},
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
        "wins": {"type": "pitching", "label": "W", "active": True},
        "losses": {"type": "pitching", "label": "L", "active": True},
        "inningsPitched": {"type": "pitching", "label": "IP", "active": False},
        "pitchingStrikeOuts": {"type": "pitching", "label": "K", "active": False},
        "era": {"type": "pitching", "label": "ERA", "active": True},
    }
}

