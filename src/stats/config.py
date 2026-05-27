
##this is twofold
##1) determining which stats need to be ordered in which direction based on hitting and pitching (ERA, for example. Lower is better.)
##2) all stats here are on the list of stats that can be randomly called in main.py for rendering the leaderboards

STAT_CONFIG = {
    "avg":                  {"ascending": False, "type": "hitting",  "label": "Batting Average"},
    "ops":                  {"ascending": False, "type": "hitting",  "label": "On-base + Slugging"},
    "obp":                  {"ascending": False, "type": "hitting",  "label": "On-Base %"},
    "slg":                  {"ascending": False, "type": "hitting",  "label": "Slugging %"},
    "homeRuns":             {"ascending": False, "type": "hitting",  "label": "Home Runs"},
    "runs":                 {"ascending": False, "type": "hitting",  "label": "Runs"},
    "doubles":              {"ascending": False, "type": "hitting",  "label": "Doubles"},
    "triples":              {"ascending": False, "type": "hitting",  "label": "Triples"},
    "hits":                 {"ascending": False, "type": "hitting",  "label": "Hits"},
    "rbi":                  {"ascending": False, "type": "hitting",  "label": "RBI"},
    "stolenBases":          {"ascending": False, "type": "hitting",  "label": "Stolen Bases"},
    "baseOnBalls":          {"ascending": False, "type": "hitting",  "label": "Base on Balls"},
    "plateAppearances":     {"ascending": False, "type": "hitting",  "label": "Plate Appearances"},
    "babip":                {"ascending": False, "type": "hitting",  "label": "BABIP"},
    "strikeOuts":           {"ascending": True,  "type": "hitting",  "label": "Strikeouts"},
    "groundIntoDoublePlay": {"ascending": True,  "type": "hitting",  "label": "GIDP"},

    "era":                  {"ascending": True,  "type": "pitching", "label": "Earned Run Average"},
    "whip":                 {"ascending": True,  "type": "pitching", "label": "WHIP"},
    "wins":                 {"ascending": False, "type": "pitching", "label": "Wins"},
    "saves":                {"ascending": False, "type": "pitching", "label": "Saves"},
    "pitchingStrikeOuts":   {"ascending": False, "type": "pitching", "label": "Strikeouts"},
    "strikeoutsPer9Inn":    {"ascending": False, "type": "pitching", "label": "K/9"},
    "inningsPitched":       {"ascending": False, "type": "pitching", "label": "Innings Pitched"},
    "gamesPitched":         {"ascending": False, "type": "pitching", "label": "Appearances"},
    "gamesStarted":         {"ascending": False, "type": "pitching", "label": "Games Started"},
    "strikePercentage":     {"ascending": False, "type": "pitching", "label": "Strike %"},
    "walksPer9Inn":         {"ascending": True,  "type": "pitching", "label": "BB/9"},
    "hitsPer9Inn":          {"ascending": True,  "type": "pitching", "label": "H/9"},
    "homeRunsPer9":         {"ascending": True,  "type": "pitching", "label": "HR/9"},
    "losses":               {"ascending": True,  "type": "pitching", "label": "Losses"},
    "blownSaves":           {"ascending": True,  "type": "pitching", "label": "Blown Saves"},
    "earnedRuns":           {"ascending": True,  "type": "pitching", "label": "Earned Runs "},
}