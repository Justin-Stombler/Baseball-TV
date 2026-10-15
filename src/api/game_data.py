import statsapi
from datetime import datetime, timedelta
from ..constants import GAME_DAY_TIMEZONE
from ..config import POSTSEASON_GAME_TYPES


def fetch_team_game(team_id: int) -> dict | None:
    """Find a team's completed game from the prior game day (yesterday, Eastern date).
    Returns None if the team didn't play a Final game yesterday, rather than falling
    back to an older game."""
    yesterday = (datetime.now(GAME_DAY_TIMEZONE) - timedelta(days=1)).strftime('%m/%d/%Y')
    games = statsapi.schedule(team=team_id, start_date=yesterday, end_date=yesterday)
    if not games:
        return None

    ##prefer the latest game_num in case of doubleheaders
    games.sort(key=lambda g: g.get('game_num', 1))

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


def fetch_games_today() -> list[dict]:
    """Fetch today's full MLB schedule, including postseason round and series status."""
    today = datetime.now(GAME_DAY_TIMEZONE).strftime('%m/%d/%Y')
    return statsapi.schedule(date=today)


def fetch_box_score(game_id: int) -> dict:
    """Fetch inning-by-inning box score data, plus pitcher decisions, for a single game."""
    data = statsapi.get('game', {'gamePk': game_id})
    raw_decisions = data['liveData'].get('decisions', {})
    decisions = {
        side: ({'name': raw_decisions[side]['fullName']} if raw_decisions.get(side) else None)
        for side in ('winner', 'loser', 'save')
    }
    return {
        'linescore': data['liveData']['linescore'],
        'home_name': data['gameData']['teams']['home']['name'],
        'away_name': data['gameData']['teams']['away']['name'],
        'decisions': decisions,
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


def fetch_player_recent_games(player_id: int, group: str = "hitting", season: int = 2026, count: int = 5) -> list[dict]:
    """Fetch a player's most recent game log entries (most recent first).

    ARGUMENTS
        player_id: MLB player id.
        group: "hitting" or "pitching".
        season: season year to pull the game log from.
        count: how many of the most recent games to return.

    Returns an empty list if the player has no game log entries yet this season.
    """
    game_types = {"R": None, **POSTSEASON_GAME_TYPES}
    splits_by_game_id = {}

    for game_type, round_name in game_types.items():
        game_type_filter = f",gameType={game_type}" if round_name else ""
        data = statsapi.get('people', {
            'personIds': player_id,
            'hydrate': f'stats(group=[{group}],type=[gameLog],season={season}{game_type_filter})',
        })
        people = data.get('people') or []
        if not people:
            continue

        stats_groups = people[0].get('stats') or []
        splits = stats_groups[0].get('splits') if stats_groups else []
        for split in splits or []:
            game_id = (split.get('game') or {}).get('gamePk')
            if game_id is None:
                continue
            splits_by_game_id[game_id] = {
                'date': split.get('date'),
                'opponent': (split.get('opponent') or {}).get('name'),
                'is_home': split.get('isHome'),
                'is_win': split.get('isWin'),
                'game_type': game_type,
                'round': round_name,
                'stats': split.get('stat', {}),
            }

    recent_games = sorted(
        splits_by_game_id.values(),
        key=lambda game: game.get('date') or '',
        reverse=True,
    )
    return recent_games[:count]


if __name__ == "__main__":
    game = fetch_team_game(147)  # Yankees
    print(game)

    today_game = fetch_team_game_today(147)
    print(today_game)

    recent_games = fetch_player_recent_games(592450, group="hitting")  # Aaron Judge
    print(recent_games)
