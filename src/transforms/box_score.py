from datetime import datetime
from zoneinfo import ZoneInfo

from ..api.game_data import fetch_team_game, fetch_box_score, fetch_team_game_today, fetch_live_game_state, fetch_probable_pitchers
from ..api.team_performance import fetch_team_performance
from ..constants import GAME_DAY_TIMEZONE, CUTOVER_TIME, classify_game_status


def _ordinal_inning(n: int) -> str:
    """Format an inning number with its ordinal suffix, e.g. 5 -> '5TH'."""
    if 10 <= n % 100 <= 20:
        suffix = "TH"
    else:
        suffix = {1: "ST", 2: "ND", 3: "RD"}.get(n % 10, "TH")
    return f"{n}{suffix}"


def _format_first_pitch(game_datetime: str | None) -> str:
    """Format a UTC ISO game_datetime as e.g. '7:05 PM ET'."""
    if not game_datetime:
        return "TBD"
    try:
        dt_utc = datetime.strptime(game_datetime, "%Y-%m-%dT%H:%M:%SZ")
        dt_eastern = dt_utc.replace(tzinfo=ZoneInfo("UTC")).astimezone(GAME_DAY_TIMEZONE)
        return dt_eastern.strftime("%-I:%M %p ET")
    except Exception:
        return "TBD"


def _format_probable(probable: dict | None) -> str:
    """Format a probable-pitcher dict as e.g. 'Sale 12-8, 2.16'. Long (e.g. hyphenated)
    last names are capped at 10 chars so they don't crowd the first-pitch time."""
    if not probable or not probable.get('name'):
        return "TBD"
    name = probable['name']
    parts = name.split(" ", 1)
    short_name = parts[1] if len(parts) > 1 else parts[0]
    if len(short_name) > 10:
        short_name = short_name[:10] + "."
    wins = probable.get('wins', 0)
    losses = probable.get('losses', 0)
    era = probable.get('era', '-.--')
    return f"{short_name} ({wins}-{losses}, {era})"


def _format_decisions(decisions: dict | None) -> str:
    """Format a final game's pitcher decisions as e.g. 'W: Molina  L: Elder  S: Senga'."""
    if not decisions:
        return ""
    labels = []
    for prefix, side in (("W", "winner"), ("L", "loser"), ("S", "save")):
        person = decisions.get(side)
        name = person.get('name') if person else None
        if not name:
            continue
        parts = name.split(" ", 1)
        short_name = parts[1] if len(parts) > 1 else parts[0]
        labels.append(f"{prefix}: {short_name}")
    return "  ".join(labels)


def _format_final_status(innings: list, scheduled_innings: int) -> str:
    """Format a final game's status label as e.g. 'FINAL' or 'FINAL/10' (extra innings
    or a shortened game)."""
    played = len(innings)
    return f"FINAL/{played}" if played and played != scheduled_innings else "FINAL"


def _format_live_status(inning_state: str | None, current_inning: int | None) -> str:
    """Format a live game's status label as e.g. 'TOP 5TH'."""
    if not inning_state or not current_inning:
        return ""
    return f"{inning_state.upper()} {_ordinal_inning(current_inning)}"


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
    scheduled_innings = linescore.get('scheduledInnings', 9)
    decisions = data.get('decisions', {})

    return {
        'game_id': game_id,
        'away_name': data['away_name'],
        'home_name': data['home_name'],
        'status': 'final',
        'game_datetime': game_datetime,
        'scheduled_innings': scheduled_innings,
        'innings': innings,
        'away_runs': away_totals.get('runs', 0),
        'away_hits': away_totals.get('hits', 0),
        'away_errors': away_totals.get('errors', 0),
        'home_runs': home_totals.get('runs', 0),
        'home_hits': home_totals.get('hits', 0),
        'home_errors': home_totals.get('errors', 0),
        'decisions': decisions,
        'status_display': _format_final_status(innings, scheduled_innings),
        'decisions_display': _format_decisions(decisions),
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
        game_status = classify_game_status(status)
        if game_status == "upcoming":
            probables = fetch_probable_pitchers(today_game['game_id'])
            away_probable = probables.get('away')
            home_probable = probables.get('home')
            return {
                'game_id': today_game['game_id'],
                'away_name': today_game['away_name'],
                'home_name': today_game['home_name'],
                'status': 'upcoming',
                'game_datetime': today_game.get('game_datetime'),
                'away_probable': away_probable,
                'home_probable': home_probable,
                'first_pitch_display': _format_first_pitch(today_game.get('game_datetime')),
                'away_probable_display': _format_probable(away_probable),
                'home_probable_display': _format_probable(home_probable),
            }
        if game_status == "live":
            state = fetch_live_game_state(today_game['game_id'])
            inning_state = state.get('inning_state')
            current_inning = state.get('current_inning')
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
                'current_inning': current_inning,
                'inning_state': inning_state,
                'status_display': _format_live_status(inning_state, current_inning),
            }
        if game_status == "final":
            return _final_box_score(today_game['game_id'], today_game.get('game_datetime'))

        ##today's game exists but isn't upcoming/live/final (e.g. postponed, cancelled,
        ##forfeited) — no fallback to an older game past the cutover
        return None

    return _completed_box_score(team_id)


def _bucket_games_by_league() -> dict[str, list[dict]]:
    """Fetch every team's current game once and bucket each unique game into 'AL'
    (both teams AL), 'NL' (both teams NL), or 'Interleague' (one team from each
    league), so a single pass over all 30 teams covers every group with no game
    ever appearing in more than one bucket."""
    league_map = {"American League": "AL", "National League": "NL"}
    rows = fetch_team_performance()
    team_league = {
        r['team_name']: league_map.get(r['league_name'], r['league_name'])
        for r in rows
        if r.get('team_name')
    }

    grouped: dict[str, list[dict]] = {"AL": [], "NL": [], "Interleague": []}
    seen_game_ids = set()
    for row in rows:
        team_id = row.get('team_id')
        team_name = row.get('team_name')
        if not team_id or not team_name:
            continue
        box_score = generate_box_score(team_id, team_name)
        if not box_score or box_score['game_id'] in seen_game_ids:
            continue
        seen_game_ids.add(box_score['game_id'])

        away_league = team_league.get(box_score['away_name'])
        home_league = team_league.get(box_score['home_name'])
        if away_league and home_league and away_league != home_league:
            matchup_group = "Interleague"
        else:
            matchup_group = away_league or home_league
        if matchup_group in grouped:
            grouped[matchup_group].append(box_score)

    ##always show games in chronological order of first pitch, regardless of status
    for games in grouped.values():
        games.sort(key=lambda g: g.get('game_datetime') or "")

    return grouped


def paginate_box_scores(games: list[dict], per_page: int) -> list[list[dict]]:
    """Split a list of games into pages of at most `per_page` games each."""
    return [games[i:i + per_page] for i in range(0, len(games), per_page)]


def generate_box_score_pages(per_page: int) -> list[dict]:
    """Build every league group's box-score pages for the day, in AL -> NL ->
    Interleague order (groups with no games are skipped entirely). Each entry is
    ready to render+display in sequence: {league_group, games, page, total_pages}."""
    grouped = _bucket_games_by_league()

    pages = []
    for league_group in ("AL", "NL", "Interleague"):
        games = grouped.get(league_group) or []
        if not games:
            continue
        group_pages = paginate_box_scores(games, per_page=per_page)
        for page_num, page_games in enumerate(group_pages, start=1):
            pages.append({
                'league_group': league_group,
                'games': page_games,
                'page': page_num,
                'total_pages': len(group_pages),
            })
    return pages
