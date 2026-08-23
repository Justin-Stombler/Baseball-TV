from datetime import datetime

from ..api.game_data import fetch_team_game, fetch_box_score, fetch_team_game_today, fetch_live_game_state, fetch_probable_pitchers
from ..api.team_performance import fetch_team_performance
from ..constants import GAME_DAY_TIMEZONE, CUTOVER_TIME, UPCOMING_STATUSES, LIVE_STATUSES, FINAL_STATUSES


def _final_box_score(game_id: int, game_datetime: str | None) -> dict:
    """Build a 'final' box score row from a game's box score data."""
    data = fetch_box_score(game_id)
    linescore = data['linescore']

    innings = []
    for inning in linescore.get('innings', []):
        innings.append({
            'num': inning['num'],
            'away_runs': inning.get('away', {}).get('runs'),
            'home_runs': inning.get('home', {}).get('runs'),
        })

    away_totals = linescore.get('teams', {}).get('away', {})
    home_totals = linescore.get('teams', {}).get('home', {})

    return {
        'game_id': game_id,
        'away_name': data['away_name'],
        'home_name': data['home_name'],
        'status': 'final',
        'game_datetime': game_datetime,
        'scheduled_innings': linescore.get('scheduledInnings', 9),
        'innings': innings,
        'away_runs': away_totals.get('runs', 0),
        'away_hits': away_totals.get('hits', 0),
        'away_errors': away_totals.get('errors', 0),
        'home_runs': home_totals.get('runs', 0),
        'home_hits': home_totals.get('hits', 0),
        'home_errors': home_totals.get('errors', 0),
    }


def _completed_box_score(team_id: int) -> dict | None:
    """Build a 'final' box score row for a team's most recently completed game."""
    game = fetch_team_game(team_id)
    if not game:
        return None
    return _final_box_score(game['game_id'], game.get('game_datetime'))


def generate_box_score(team_id: int, team_name: str) -> dict | None:
    """Build a box score row for a team's game. Before the cutover time (ET), always
    shows the most recently completed game. After the cutover, only shows today's game
    ('upcoming' shows first-pitch time instead of innings, 'live' shows the partial
    box score); if the team has no game today, returns None rather than falling back
    to an older completed game."""
    now_eastern = datetime.now(GAME_DAY_TIMEZONE)
    if now_eastern.time() >= CUTOVER_TIME:
        today_game = fetch_team_game_today(team_id)
        if not today_game:
            return None

        status = today_game['status']
        if status in UPCOMING_STATUSES:
            probables = fetch_probable_pitchers(today_game['game_id'])
            return {
                'game_id': today_game['game_id'],
                'away_name': today_game['away_name'],
                'home_name': today_game['home_name'],
                'status': 'upcoming',
                'game_datetime': today_game.get('game_datetime'),
                'away_probable': probables.get('away'),
                'home_probable': probables.get('home'),
            }
        if status in LIVE_STATUSES:
            state = fetch_live_game_state(today_game['game_id'])
            return {
                'game_id': state['game_id'],
                'away_name': state['away_name'],
                'home_name': state['home_name'],
                'status': 'live',
                'game_datetime': today_game.get('game_datetime'),
                'scheduled_innings': state['scheduled_innings'],
                'innings': state['innings'],
                'away_runs': state['away_runs'],
                'away_hits': state['away_hits'],
                'away_errors': state['away_errors'],
                'home_runs': state['home_runs'],
                'home_hits': state['home_hits'],
                'home_errors': state['home_errors'],
                'current_inning': state.get('current_inning'),
                'inning_state': state.get('inning_state'),
            }
        if status in FINAL_STATUSES:
            return _final_box_score(today_game['game_id'], today_game.get('game_datetime'))

        ##today's game exists but isn't upcoming/live/final (e.g. postponed) — no
        ##fallback to an older game past the cutover
        return None

    return _completed_box_score(team_id)


def generate_division_box_scores(league: str, division: str, count: int = 5) -> list[dict]:
    """Build box scores for each team's most recently completed game across one division
    (max 5 teams/games, one per team)."""
    league_map = {"AL": "American League", "NL": "National League"}
    full_league = league_map.get(league, league)
    division_lower = division.lower().strip()

    rows = fetch_team_performance()
    teams = [
        r for r in rows
        if r.get("league_name") == full_league
        and division_lower in (r.get("division_name") or "").lower()
    ]
    teams = sorted(teams, key=lambda r: r.get("division_rank") or 999)
    division_team_names = {t.get('team_name') for t in teams}

    games = []
    seen_game_ids = set()
    for team in teams:
        if len(games) >= count:
            break
        team_id = team.get('team_id')
        team_name = team.get('team_name')
        if not team_id or not team_name:
            continue
        box_score = generate_box_score(team_id, team_name)
        if not box_score or box_score['game_id'] in seen_game_ids:
            continue
        seen_game_ids.add(box_score['game_id'])
        box_score['away_in_division'] = box_score['away_name'] in division_team_names
        box_score['home_in_division'] = box_score['home_name'] in division_team_names
        games.append(box_score)

    ##always show games in chronological order of first pitch, regardless of status
    games.sort(key=lambda g: g.get('game_datetime') or "")

    return games
