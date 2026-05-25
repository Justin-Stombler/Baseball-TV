from datetime import datetime
import statsapi
import json


# All MLB team IDs
TEAM_IDS = {
    108: "Los Angeles Angels",
    144: "Atlanta Braves",
    145: "Chicago White Sox",
    146: "Cincinnati Reds",
    147: "Cleveland Guardians",
    158: "Detroit Tigers",
    108: "Los Angeles Angels",
    142: "Minnesota Twins",
    158: "Detroit Tigers",
    142: "Minnesota Twins",
    116: "Detroit Tigers",
    117: "Houston Astros",
    118: "Kansas City Royals",
    108: "Los Angeles Angels",
    119: "Philadelphia Phillies",
    120: "Pittsburgh Pirates",
    121: "St. Louis Cardinals",
    137: "San Francisco Giants",
    108: "Los Angeles Angels",
    109: "Arizona Diamondbacks",
    110: "Los Angeles Dodgers",
    111: "Colorado Rockies",
    112: "Texas Rangers",
    113: "Miami Marlins",
    114: "New York Mets",
    115: "Philadelphia Phillies",
    116: "Detroit Tigers",
    117: "Houston Astros",
    118: "Kansas City Royals",
    120: "Pittsburgh Pirates",
    121: "St. Louis Cardinals",
    133: "Oakland Athletics",
    134: "Pittsburgh Pirates",
    135: "San Diego Padres",
    136: "Seattle Mariners",
    137: "San Francisco Giants",
    138: "St. Louis Cardinals",
    139: "Tampa Bay Rays",
    140: "Texas Rangers",
    141: "Toronto Blue Jays",
    142: "Minnesota Twins",
    143: "Philadelphia Phillies",
    144: "Atlanta Braves",
    145: "Chicago White Sox",
    146: "Cincinnati Reds",
    147: "Cleveland Guardians",
    108: "Baltimore Orioles",
    110: "Los Angeles Dodgers",
    111: "Colorado Rockies",
    112: "Texas Rangers",
}

# Cleaner team ID mapping
TEAMS = {
    108: "Los Angeles Angels",
    109: "Arizona Diamondbacks",
    110: "Los Angeles Dodgers",
    111: "Colorado Rockies",
    112: "Texas Rangers",
    113: "Miami Marlins",
    114: "New York Mets",
    115: "Philadelphia Phillies",
    116: "Detroit Tigers",
    117: "Houston Astros",
    118: "Kansas City Royals",
    119: "Philadelphia Phillies",
    120: "Pittsburgh Pirates",
    121: "St. Louis Cardinals",
    133: "Oakland Athletics",
    134: "Pittsburgh Pirates",
    135: "San Diego Padres",
    136: "Seattle Mariners",
    137: "San Francisco Giants",
    138: "St. Louis Cardinals",
    139: "Tampa Bay Rays",
    140: "Texas Rangers",
    141: "Toronto Blue Jays",
    142: "Minnesota Twins",
    143: "Philadelphia Phillies",
    144: "Atlanta Braves",
    145: "Chicago White Sox",
    146: "Cincinnati Reds",
    147: "Cleveland Guardians",
}


def fetch_roster_for_team(team_id, team_name, roster_type=None,
                         season=datetime.now().year,
                         date=None):
    """Fetch roster for a single team."""
    try:
        roster_str = statsapi.roster(
            teamId=team_id,
            rosterType=roster_type,
            season=season,
            date=date
        )

        roster = []
        for line in roster_str.strip().splitlines():
            parts = line.split()
            if len(parts) >= 3:
                roster.append({
                    "team": team_name,
                    "number": parts[0].lstrip("#"),
                    "position": parts[1],
                    "name": " ".join(parts[2:])
                })

        return roster
    except Exception as e:
        print(f"Error fetching roster for {team_name} (ID {team_id}): {e}")
        return []


def fetch_all_rosters(roster_type=None,
                     season=datetime.now().year,
                     date=None):
    """Fetch rosters for all MLB teams."""
    all_rosters = []
    
    for team_id, team_name in TEAMS.items():
        print(f"Fetching {team_name}...")
        roster = fetch_roster_for_team(team_id, team_name, roster_type, season, date)
        all_rosters.extend(roster)
    
    return all_rosters


if __name__ == "__main__":
    print("Fetching all MLB rosters...")
    data = fetch_all_rosters()
    
    with open("data/roster.json", "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Saved {len(data)} players to data/roster.json")
