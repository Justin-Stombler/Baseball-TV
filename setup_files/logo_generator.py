import requests
import statsapi
import os

os.makedirs("logos", exist_ok=True)

teams = statsapi.get('teams', {'sportId': 1}) #baseball

##below loop runs across every team to download all MLB logos one time, required for repository.

for team in teams['teams']:
    team_id = team['id']
    team_name = team['name']
    
    urls = [
        f"https://midfield.mlbstatic.com/v1/team/{team_id}/spots/500",
        f"https://www.mlbstatic.com/team-logos/{team_id}.svg",
    ]
    
    saved = False
    for url in urls:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            ext = "png" if "midfield" in url else "svg"
            with open(f"logos/{team_name}.{ext}", 'wb') as f:
                f.write(r.content)
            print(f"saved {team_name} ({ext})")
            saved = True
            break
    
    if not saved:
        print(f"FAILED {team_name}")