from ..api.team_performance import fetch_team_performance


def generate_standings(season: int = 2026, standings_type: str = "regularSeason") -> list[dict]:
	"""Return standings rows trimmed to the fields needed for a division standings render."""
	rows = fetch_team_performance(season=season, standings_type=standings_type)
	return [
		{
			"league_name": r.get("league_name"),
			"division_name": r.get("division_name"),
			"team_name": r.get("team_name"),
			"wins": r.get("wins"),
			"losses": r.get("losses"),
			"pct": r.get("pct"),
			"division_games_back": r.get("division_games_back"),
			"streak": r.get("streak"),
			"last_ten": r.get("last_ten"),
		}
		for r in rows
	]


def _pct_to_float(value) -> float:
	"""Safely convert pct values like '.612' to float for sorting."""
	try:
		return float(value)
	except (TypeError, ValueError):
		return -1.0


def _league_name(league: str) -> str:
	league_map = {
		"AL": "American League",
		"NL": "National League",
	}
	return league_map.get(league, league)


def select_division_standings(
	rows: list[dict],
	league: str,
	division: str,
) -> list[dict]:
	"""Filter standings rows to one league/division and sort by pct descending."""
	full_league = _league_name(league)
	division_lower = division.lower().strip()
	filtered = [
		r
		for r in rows
		if (r.get("league_name") == full_league)
		and (division_lower in (r.get("division_name") or "").lower())
	]
	return sorted(filtered, key=lambda r: _pct_to_float(r.get("pct")), reverse=True)


def get_division_teams(rows: list[dict], league: str, division: str) -> list[str]:
	"""Return team names for one division from a full standings dataset."""
	return [r.get("team_name") for r in select_division_standings(rows, league, division)]


def generate_division_standings(
	league: str,
	division: str,
	season: int = 2026,
	standings_type: str = "regularSeason",
) -> list[dict]:
	"""Convenience wrapper: fetch full standings then select one division."""
	rows = generate_standings(season=season, standings_type=standings_type)
	return select_division_standings(rows=rows, league=league, division=division)


if __name__ == "__main__":
	import json
	print(json.dumps(generate_standings(), indent=2))
