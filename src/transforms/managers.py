from ..api.jobs import fetch_jobs


def generate_manager_list(season: int = 2026) -> list[dict]:
    """Transform coaching staff data into a list of managers only.

    A team can have both a 'Manager' and an 'Interim Manager' listed at once
    when a mid-season change happens (statsapi keeps the outgoing manager's
    entry around). Interim Manager, being the currently active one, wins.
    """
    staff = fetch_jobs(season=season)

    managers_by_team: dict = {}
    for person in staff:
        job = person.get('job')
        if job not in ('Manager', 'Interim Manager'):
            continue
        team = person.get('teamName')
        # Interim Manager takes precedence over Manager for the same team.
        if team in managers_by_team and managers_by_team[team]['jobTitle'] == 'Interim Manager' and job != 'Interim Manager':
            continue
        managers_by_team[team] = {
            'id': person.get('person', {}).get('id'),
            'name': person.get('person', {}).get('fullName'),
            'team': team,
            'teamId': person.get('teamId'),
            'jobTitle': job,
        }

    return list(managers_by_team.values())


if __name__ == "__main__":
    managers = generate_manager_list()
    print(f"Fetched {len(managers)} managers")
    for m in managers:
        print(f"  {m['name']} - {m['team']}")

