import statsapi
from datetime import datetime, timedelta

def fetch_team_schedule(team_id: int, days_back: int = 10, days_forward: int = 15) -> list:
    """Fetch a team's schedule window (past + future games) around today."""
    today = datetime.now()
    start_date = (today - timedelta(days=days_back)).strftime('%m/%d/%Y')
    end_date = (today + timedelta(days=days_forward)).strftime('%m/%d/%Y')

    return statsapi.schedule(team=team_id, start_date=start_date, end_date=end_date)


def fetch_pitcher_record(name: str) -> str:
    """Look up a pitcher's current-season win-loss record, e.g. '8-8'."""
    if not name:
        return ""

    try:
        matches = statsapi.lookup_player(name)
        if not matches:
            return ""
        stats = statsapi.player_stat_data(matches[0]['id'], group='pitching', type='season')
        season_stats = stats.get('stats', [{}])[0].get('stats', {})
        wins = season_stats.get('wins')
        losses = season_stats.get('losses')
        if wins is not None and losses is not None:
            return f"{wins}-{losses}"
    except Exception:
        pass

    return ""
