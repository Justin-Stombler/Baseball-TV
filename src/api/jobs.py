import statsapi

def fetch_jobs(season: int = 2026) -> list[dict]:
    """Fetch all managers and coaches for every MLB team."""
    teams = statsapi.get('teams', {'sportIds': 1, 'season': season})
    
    staff = []
    for team in teams.get('teams', []):
        roster = statsapi.get('team_roster', {
            'teamId': team['id'],
            'rosterType': 'coach',
            'season': season,
        })
        for person in roster.get('roster', []):
            person['teamId'] = team['id']
            person['teamName'] = team['name']
            staff.append(person)
    
    return staff

if __name__ == "__main__":
    staff = fetch_jobs(season=2026)
    print(f"Fetched {len(staff)} coaches/managers")
    print(staff)