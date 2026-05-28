
##this is twofold
##1) determining which stats need to be ordered in which direction based on hitting and pitching (ERA, for example. Lower is better.)
##2) all stats here are on the list of stats that can be randomly called in main.py for rendering the leaderboards

STAT_CONFIG = {
    "avg":                  {"ascending": False, "type": "hitting",  "label": "AVG", "active": True},
    "ops":                  {"ascending": False, "type": "hitting",  "label": "OPS", "active": True},
    "obp":                  {"ascending": False, "type": "hitting",  "label": "OBP", "active": True},
    "slg":                  {"ascending": False, "type": "hitting",  "label": "Slugging %", "active": True},
    "homeRuns":             {"ascending": False, "type": "hitting",  "label": "HR", "active": True},
    "runs":                 {"ascending": False, "type": "hitting",  "label": "Runs", "active": True},
    "doubles":              {"ascending": False, "type": "hitting",  "label": "Doubles", "active": True},
    "triples":              {"ascending": False, "type": "hitting",  "label": "Triples", "active": True},
    "hits":                 {"ascending": False, "type": "hitting",  "label": "Hits", "active": True},
    "rbi":                  {"ascending": False, "type": "hitting",  "label": "RBI", "active": True},
    "stolenBases":          {"ascending": False, "type": "hitting",  "label": "Stolen Bases", "active": True},
    "baseOnBalls":          {"ascending": False, "type": "hitting",  "label": "Base on Balls", "active": True},
    "plateAppearances":     {"ascending": False, "type": "hitting",  "label": "Plate Appearances", "active": True},
    "babip":                {"ascending": False, "type": "hitting",  "label": "BABIP", "active": True},
    "strikeOuts":           {"ascending": True,  "type": "hitting",  "label": "Strikeouts", "active": True},
    "groundIntoDoublePlay": {"ascending": False,  "type": "hitting",  "label": "GIDP", "active": True},

    "era":                  {"ascending": True,  "type": "pitching", "label": "ERA", "active": True},
    "whip":                 {"ascending": True,  "type": "pitching", "label": "WHIP", "active": True},
    "wins":                 {"ascending": False, "type": "pitching", "label": "Wins", "active": True},
    "saves":                {"ascending": False, "type": "pitching", "label": "Saves", "active": True},
    "pitchingStrikeOuts":   {"ascending": False, "type": "pitching", "label": "SO", "active": True},
    "strikeoutsPer9Inn":    {"ascending": False, "type": "pitching", "label": "K/9", "active": True},
    "inningsPitched":       {"ascending": False, "type": "pitching", "label": "IP", "active": True},
    "gamesPitched":         {"ascending": False, "type": "pitching", "label": "Appearances", "active": True},
    "gamesStarted":         {"ascending": False, "type": "pitching", "label": "Games Started", "active": False},
    "strikePercentage":     {"ascending": False, "type": "pitching", "label": "Strike %", "active": True},
    "walksPer9Inn":         {"ascending": True,  "type": "pitching", "label": "BB/9", "active": True},
    "hitsPer9Inn":          {"ascending": True,  "type": "pitching", "label": "H/9", "active": True},
    "homeRunsPer9":         {"ascending": True,  "type": "pitching", "label": "HR/9", "active": True},
    "losses":               {"ascending": True,  "type": "pitching", "label": "Losses", "active": True},
    "blownSaves":           {"ascending": False,  "type": "pitching", "label": "Blown Saves", "active": False},
    "earnedRuns":           {"ascending": False,  "type": "pitching", "label": "Earned Runs ", "active": True},
}