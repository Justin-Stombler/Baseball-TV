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
			"streak": r.get("streak"),
			"last_ten": r.get("last_ten"),
		}
		for r in rows
	]


if __name__ == "__main__":
	import json
	print(json.dumps(generate_standings(), indent=2))
