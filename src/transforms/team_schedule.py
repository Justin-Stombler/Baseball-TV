from ..api.team_schedule import fetch_team_schedule, fetch_pitcher_record

def get_pitcher_record(name: str, cache: dict) -> str:
    """Look up a pitcher's current-season win-loss record, caching by name within a call."""
    if not name:
        return ""
    if name in cache:
        return cache[name]

    record = fetch_pitcher_record(name)
    cache[name] = record
    return record


def generate_team_schedule(team_id: int, team_name: str) -> dict:
    """Build a team's last 5 completed games and next 3 games (including any in-progress game)."""
    games = fetch_team_schedule(team_id)
    pitcher_record_cache: dict = {}

    past = []
    future = []
    for g in games:
        is_home = g['home_id'] == team_id
        opponent = g['away_name'] if is_home else g['home_name']
        team_score = g['home_score'] if is_home else g['away_score']
        opponent_score = g['away_score'] if is_home else g['home_score']

        entry = {
            'opponent': opponent,
            'home_away': 'vs' if is_home else '@',
            'away_team': g['away_name'],
            'home_team': g['home_name'],
            'date': g['game_date'],
            'game_datetime': g.get('game_datetime'),
            'status': g['status'],
            'team_score': team_score,
            'opponent_score': opponent_score,
            'winning_pitcher': g.get('winning_pitcher'),
            'losing_pitcher': g.get('losing_pitcher'),
            'probable_pitcher_team': g['home_probable_pitcher'] if is_home else g['away_probable_pitcher'],
            'probable_pitcher_opponent': g['away_probable_pitcher'] if is_home else g['home_probable_pitcher'],
        }

        if g['status'] == 'Final':
            entry['result'] = 'W' if g.get('winning_team') == team_name else 'L'
            past.append(entry)
        else:
            future.append(entry)

    past.sort(key=lambda e: e['date'])
    future.sort(key=lambda e: e['date'])

    last_5 = past[-5:]
    next_3 = future[:3]

    # Only look up pitcher records for the games actually kept, not every game in the fetch window.
    for entry in last_5:
        entry['winning_pitcher_record'] = get_pitcher_record(entry.get('winning_pitcher'), pitcher_record_cache)
        entry['losing_pitcher_record'] = get_pitcher_record(entry.get('losing_pitcher'), pitcher_record_cache)

    return {
        'team_name': team_name,
        'last_5': last_5,
        'next_3': next_3,
    }
