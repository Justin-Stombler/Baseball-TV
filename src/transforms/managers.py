from ..api.jobs import fetch_jobs


def generate_manager_list(season: int = 2026) -> list[dict]:
    """Transform coaching staff data into a list of managers only."""
    staff = fetch_jobs(season=season)

    managers = []
    for person in staff:
        if person.get('job') != 'Manager':
            continue
        managers.append({
            'id': person.get('person', {}).get('id'),
            'name': person.get('person', {}).get('fullName'),
            'team': person.get('teamName'),
            'teamId': person.get('teamId'),
            'jobTitle': person.get('job'),
        })

    return managers


if __name__ == "__main__":
    managers = generate_manager_list()
    print(f"Fetched {len(managers)} managers")
    for m in managers:
        print(f"  {m['name']} - {m['team']}")

