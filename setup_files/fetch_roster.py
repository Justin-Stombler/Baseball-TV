from datetime import datetime
import statsapi
import json


# Correct MLB team ID -> name mapping (verified against statsapi.get('teams', {'sportId': 1}))
TEAMS = {
    108: "Los Angeles Angels",
    109: "Arizona Diamondbacks",
    110: "Baltimore Orioles",
    111: "Boston Red Sox",
    112: "Chicago Cubs",
    113: "Cincinnati Reds",
    114: "Cleveland Guardians",
    115: "Colorado Rockies",
    116: "Detroit Tigers",
    117: "Houston Astros",
    118: "Kansas City Royals",
    119: "Los Angeles Dodgers",
    120: "Washington Nationals",
    121: "New York Mets",
    133: "Athletics",
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
    146: "Miami Marlins",
    147: "New York Yankees",
    158: "Milwaukee Brewers",
}


def fetch_roster_for_team(team_id, team_name, roster_type='40Man',
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


def fetch_all_rosters(roster_type='40Man',
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
