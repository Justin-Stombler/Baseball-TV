
##this is twofold
##1) determining which stats need to be ordered in which direction based on hitting and pitching (ERA, for example. Lower is better.)
##2) all stats here are on the list of stats that can be randomly called in main.py for rendering the leaderboards

STAT_CONFIG = {
    "avg":                  {"ascending": False, "type": "hitting",  "label": "AVG"},
    "ops":                  {"ascending": False, "type": "hitting",  "label": "OPS"},
    "obp":                  {"ascending": False, "type": "hitting",  "label": "OBP"},
    "slg":                  {"ascending": False, "type": "hitting",  "label": "SLG"},
    "homeRuns":             {"ascending": False, "type": "hitting",  "label": "HR"},
    "runs":                 {"ascending": False, "type": "hitting",  "label": "R"},
    "doubles":              {"ascending": False, "type": "hitting",  "label": "2B"},
    "triples":              {"ascending": False, "type": "hitting",  "label": "3B"},
    "hits":                 {"ascending": False, "type": "hitting",  "label": "H"},
    "rbi":                  {"ascending": False, "type": "hitting",  "label": "RBI"},
    "stolenBases":          {"ascending": False, "type": "hitting",  "label": "SB"},
    "baseOnBalls":          {"ascending": False, "type": "hitting",  "label": "BB"},
    "plateAppearances":     {"ascending": False, "type": "hitting",  "label": "PA"},
    "babip":                {"ascending": False, "type": "hitting",  "label": "BABIP"},
    "strikeOuts":           {"ascending": True,  "type": "hitting",  "label": "SO"},
    "groundIntoDoublePlay": {"ascending": True,  "type": "hitting",  "label": "GIDP"},

    "era":                  {"ascending": True,  "type": "pitching", "label": "ERA"},
    "whip":                 {"ascending": True,  "type": "pitching", "label": "WHIP"},
    "wins":                 {"ascending": False, "type": "pitching", "label": "W"},
    "saves":                {"ascending": False, "type": "pitching", "label": "SV"},
    "pitchingStrikeOuts":   {"ascending": False, "type": "pitching", "label": "SO"},
    "strikeoutsPer9Inn":    {"ascending": False, "type": "pitching", "label": "SO/9"},
    "inningsPitched":       {"ascending": False, "type": "pitching", "label": "IP"},
    "gamesPitched":         {"ascending": False, "type": "pitching", "label": "G"},
    "gamesStarted":         {"ascending": False, "type": "pitching", "label": "GS"},
    "strikePercentage":     {"ascending": False, "type": "pitching", "label": "STR%"},
    "walksPer9Inn":         {"ascending": True,  "type": "pitching", "label": "BB/9"},
    "hitsPer9Inn":          {"ascending": True,  "type": "pitching", "label": "H/9"},
    "homeRunsPer9":         {"ascending": True,  "type": "pitching", "label": "HR/9"},
    "losses":               {"ascending": True,  "type": "pitching", "label": "L"},
    "blownSaves":           {"ascending": True,  "type": "pitching", "label": "BS"},
    "earnedRuns":           {"ascending": True,  "type": "pitching", "label": "ER"},
}