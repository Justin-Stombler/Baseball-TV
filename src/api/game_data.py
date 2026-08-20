import statsapi
from datetime import datetime, timedelta
from ..constants import GAME_DAY_TIMEZONE


def fetch_team_game(team_id: int, days_back: int = 10) -> dict | None:
    """Find a team's most recently completed game within the lookback window."""
    today = datetime.now(GAME_DAY_TIMEZONE)
    start_date = (today - timedelta(days=days_back)).strftime('%m/%d/%Y')
    end_date = today.strftime('%m/%d/%Y')

    games = statsapi.schedule(team=team_id, start_date=start_date, end_date=end_date)
    if not games:
        return None

    games.sort(key=lambda g: g['game_date'])

    final_games = [g for g in games if g['status'] == 'Final']
    if final_games:
        return final_games[-1]

    return None


def fetch_team_game_today(team_id: int) -> dict | None:
    """Find a team's game scheduled for today (Eastern date), regardless of status."""
    today = datetime.now(GAME_DAY_TIMEZONE).strftime('%m/%d/%Y')
    games = statsapi.schedule(team=team_id, start_date=today, end_date=today)
    if not games:
        return None
    ##prefer the latest game_num in case of doubleheaders
    games.sort(key=lambda g: g.get('game_num', 1))
    return games[-1]


def fetch_box_score(game_id: int) -> dict:
    """Fetch inning-by-inning box score data for a single game."""
    data = statsapi.get('game', {'gamePk': game_id})
    return {
        'linescore': data['liveData']['linescore'],
        'home_name': data['gameData']['teams']['home']['name'],
        'away_name': data['gameData']['teams']['away']['name'],
        'status': data['gameData']['status']['detailedState'],
    }


def fetch_probable_pitchers(game_id: int) -> dict:
    """Fetch probable starting pitcher name, win-loss record, and ERA (current season)
    for both teams in a scheduled game. Either side is None if no probable is set yet."""
    data = statsapi.get('game', {'gamePk': game_id})
    probables = data['gameData'].get('probablePitchers', {})

    result = {}
    for side in ('away', 'home'):
        pitcher = probables.get(side)
        if not pitcher:
            result[side] = None
            continue
        stat_data = statsapi.player_stat_data(pitcher['id'], group='pitching', type='season')
        season_stats = (stat_data.get('stats') or [{}])[0].get('stats', {})
        result[side] = {
            'name': pitcher.get('fullName'),
            'wins': season_stats.get('wins', 0),
            'losses': season_stats.get('losses', 0),
            'era': season_stats.get('era', '-.--'),
        }
    return result


def fetch_live_game_state(game_id: int) -> dict:
    """Fetch live in-progress state: partial box score, current pitcher/batter, count,
    outs, and men-on-base context for a single game."""
    data = statsapi.get('game', {'gamePk': game_id})
    live = data['liveData']
    linescore = live['linescore']

    innings = []
    for inning in linescore.get('innings', []):
        innings.append({
            'num': inning['num'],
            'away_runs': inning.get('away', {}).get('runs'),
            'home_runs': inning.get('home', {}).get('runs'),
        })

    away_totals = linescore.get('teams', {}).get('away', {})
    home_totals = linescore.get('teams', {}).get('home', {})
    offense = linescore.get('offense', {})
    defense = linescore.get('defense', {})
    current_play = live.get('plays', {}).get('currentPlay', {})
    men_on_base = current_play.get('matchup', {}).get('splits', {}).get('menOnBase', '')

    return {
        'game_id': game_id,
        'home_name': data['gameData']['teams']['home']['name'],
        'away_name': data['gameData']['teams']['away']['name'],
        'status': data['gameData']['status']['detailedState'],
        'scheduled_innings': linescore.get('scheduledInnings', 9),
        'innings': innings,
        'away_runs': away_totals.get('runs', 0),
        'away_hits': away_totals.get('hits', 0),
        'away_errors': away_totals.get('errors', 0),
        'home_runs': home_totals.get('runs', 0),
        'home_hits': home_totals.get('hits', 0),
        'home_errors': home_totals.get('errors', 0),
        'current_inning': linescore.get('currentInning'),
        'inning_state': linescore.get('inningState'),
        'balls': linescore.get('balls', 0),
        'strikes': linescore.get('strikes', 0),
        'outs': linescore.get('outs', 0),
        'batter': (offense.get('batter') or {}).get('fullName'),
        'on_deck': (offense.get('onDeck') or {}).get('fullName'),
        'pitcher': (defense.get('pitcher') or {}).get('fullName'),
        'men_on_base': men_on_base,
    }

if __name__ == "__main__":
    game = fetch_team_game(147)  # Yankees
    print(game)

    today_game = fetch_team_game_today(147)
    print(today_game)
