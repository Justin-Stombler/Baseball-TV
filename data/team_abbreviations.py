##team abbreviations
TEAM_ABBREVIATIONS = {
    "Baltimore Orioles":       "BAL",
    "Boston Red Sox":          "BOS",
    "New York Yankees":        "NYY",
    "Tampa Bay Rays":          "TBR",
    "Toronto Blue Jays":       "TOR",
    "Chicago White Sox":       "CWS",
    "Cleveland Guardians":     "CLE",
    "Detroit Tigers":          "DET",
    "Kansas City Royals":      "KCR",
    "Minnesota Twins":         "MIN",
    "Houston Astros":          "HOU",
    "Los Angeles Angels":      "LAA",
    "Athletics":               "ATH",
    "Seattle Mariners":        "SEA",
    "Texas Rangers":           "TEX",
    "Atlanta Braves":          "ATL",
    "Miami Marlins":           "MIA",
    "New York Mets":           "NYM",
    "Philadelphia Phillies":   "PHI",
    "Washington Nationals":    "WSH",
    "Chicago Cubs":            "CHC",
    "Cincinnati Reds":         "CIN",
    "Milwaukee Brewers":       "MIL",
    "Pittsburgh Pirates":      "PIT",
    "St. Louis Cardinals":     "STL",
    "Arizona Diamondbacks":    "ARI",
    "Colorado Rockies":        "COL",
    "Los Angeles Dodgers":     "LAD",
    "San Diego Padres":        "SDP",
    "San Francisco Giants":    "SFG",
}

def get_team_abbreviation(team_name: str) -> str:
    """
    Returns the abbreviation for a given team name.
    Falls back to None if team not found.
    """
    abbreviation = TEAM_ABBREVIATIONS.get(team_name)
    return abbreviation

if __name__ == "__main__":
    print(get_team_abbreviation("New York Yankees")) 