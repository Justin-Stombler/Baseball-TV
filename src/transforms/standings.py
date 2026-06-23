from ..api.team_performance import fetch_team_performance


def generate_standings(season: int = 2026, standings_type: str = "regularSeason") -> list[dict]:
	"""Return trimmed standings rows used by the standings renders."""
	rows = fetch_team_performance(season=season, standings_type=standings_type)
	return [
		{
			"league_name": r.get("league_name"),
			"division_name": r.get("division_name"),
			"team_name": r.get("team_name"),
			"wins": r.get("wins"),
			"losses": r.get("losses"),
			"pct": r.get("pct"),
			"wild_card_rank": r.get("wild_card_rank"),
			"division_games_back": r.get("division_games_back"),
			"wild_card_games_back": r.get("wild_card_games_back"),
			"streak": r.get("streak"),
			"last_ten": r.get("last_ten"),
		}
		for r in rows
	]


def generate_wild_card_standings(
	league: str,
	season: int = 2026,
	standings_type: str = "regularSeason",
	count: int = 5,
) -> list[dict]:
	"""Return the current wild card field plus the next teams below for one league."""
	league_map = {
		"AL": "American League",
		"NL": "National League",
	}
	full_league = league_map.get(league, league)
	rows = generate_standings(season=season, standings_type=standings_type)
	filtered = [
		r
		for r in rows
		if r.get("league_name") == full_league and r.get("wild_card_rank") is not None
	]
	return sorted(
		filtered,
		key=lambda r: int(r.get("wild_card_rank", 999)),
	)[:count]


def generate_division_standings(
	league: str,
	division: str,
	season: int = 2026,
	standings_type: str = "regularSeason",
) -> list[dict]:
	"""Return standings rows for one division, sorted by winning percentage."""
	league_map = {
		"AL": "American League",
		"NL": "National League",
	}
	full_league = league_map.get(league, league)
	division_lower = division.lower().strip()
	rows = generate_standings(season=season, standings_type=standings_type)
	filtered = [
		r
		for r in rows
		if r.get("league_name") == full_league
		and division_lower in (r.get("division_name") or "").lower()
	]

	def pct_value(row: dict) -> float:
		try:
			return float(row.get("pct"))
		except (TypeError, ValueError):
			return -1.0

	return sorted(filtered, key=pct_value, reverse=True)


if __name__ == "__main__":
	import json
	print(json.dumps(generate_standings(), indent=2))
