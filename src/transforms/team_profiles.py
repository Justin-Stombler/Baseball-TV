from ..api.team_performance import fetch_team_performance


def generate_team_profile(season: int = 2026, standings_type: str = "regularSeason") -> list[dict]:
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
		for r in rows ]


if __name__ == "__main__":
	import json
	print(json.dumps(generate_team_profile(), indent=2))