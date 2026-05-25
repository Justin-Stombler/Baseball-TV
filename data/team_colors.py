##Generated with Claude:

TEAM_COLORS = {
    # AL East
    "Baltimore Orioles":       {"primary": "#DF4601", "secondary": "#000000"},
    "Boston Red Sox":          {"primary": "#BD3039", "secondary": "#0C2340"},
    "New York Yankees":        {"primary": "#132448", "secondary": "#C4CED4"},
    "Tampa Bay Rays":          {"primary": "#092C5C", "secondary": "#8FBCE6"},
    "Toronto Blue Jays":       {"primary": "#134A8E", "secondary": "#1D2D5C"},

    # AL Central
    "Chicago White Sox":       {"primary": "#27251F", "secondary": "#C4CED4"},
    "Cleveland Guardians":     {"primary": "#E31937", "secondary": "#0C2340"},
    "Detroit Tigers":          {"primary": "#0C2340", "secondary": "#FA4616"},
    "Kansas City Royals":      {"primary": "#004687", "secondary": "#BD9B60"},
    "Minnesota Twins":         {"primary": "#002B5C", "secondary": "#D31145"},

    # AL West
    "Houston Astros":          {"primary": "#002D62", "secondary": "#EB6E1F"},
    "Los Angeles Angels":      {"primary": "#BA0021", "secondary": "#003263"},
    "Oakland Athletics":       {"primary": "#003831", "secondary": "#EFB21E"},
    "Seattle Mariners":        {"primary": "#0C2C56", "secondary": "#005C5C"},
    "Texas Rangers":           {"primary": "#003278", "secondary": "#C0111F"},

    # NL East
    "Atlanta Braves":          {"primary": "#13274F", "secondary": "#CE1141"},
    "Miami Marlins":           {"primary": "#000000", "secondary": "#0077C8"},
    "New York Mets":           {"primary": "#002D72", "secondary": "#FF5910"},
    "Philadelphia Phillies":   {"primary": "#E81828", "secondary": "#002D72"},
    "Washington Nationals":    {"primary": "#AB0003", "secondary": "#14225A"},

    # NL Central
    "Chicago Cubs":            {"primary": "#0E3386", "secondary": "#CC3433"},
    "Cincinnati Reds":         {"primary": "#C6011F", "secondary": "#000000"},
    "Milwaukee Brewers":       {"primary": "#12284B", "secondary": "#FFC52F"},
    "Pittsburgh Pirates":      {"primary": "#27251F", "secondary": "#FDB827"},
    "St. Louis Cardinals":     {"primary": "#C41E3A", "secondary": "#0C2340"},

    # NL West
    "Arizona Diamondbacks":    {"primary": "#A71930", "secondary": "#E3D4AD"},
    "Colorado Rockies":        {"primary": "#33006F", "secondary": "#000000"},
    "Los Angeles Dodgers":     {"primary": "#005A9C", "secondary": "#FFFFFF"},
    "San Diego Padres":        {"primary": "#2F241D", "secondary": "#A2AAAD"},
    "San Francisco Giants":    {"primary": "#FD5A1E", "secondary": "#27251F"},
}


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color string to RGB tuple for Pillow."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def get_team_colors(team_name: str) -> dict:
    """
    Returns primary and secondary colors as RGB tuples for a given team name.
    Falls back to neutral colors if team not found.
    """
    colors = TEAM_COLORS.get(team_name, {"primary": "#FFFFFF", "secondary": "#888888"})
    return {
        "primary": hex_to_rgb(colors["primary"]),
        "secondary": hex_to_rgb(colors["secondary"]),
    }