import statsapi

def fetch_team_hitting_stats(season: int = 2026) -> dict:
	"""Fetch official team-level season hitting totals, keyed by team name.

	Uses MLB's team stats endpoint so a traded player's production is credited
	to whichever team he actually earned it with, instead of being lumped onto
	his current roster team.
	"""
	data = statsapi.get("teams_stats", {
		"stats": "season",
		"group": "hitting",
		"season": season,
		"gameType": "R",
		"sportIds": 1,
	})
	splits = data["stats"][0]["splits"]
	return {s["team"]["name"]: s["stat"] for s in splits}


def fetch_team_pitching_stats(season: int = 2026) -> dict:
	"""Fetch official team-level season pitching totals, keyed by team name."""
	data = statsapi.get("teams_stats", {
		"stats": "season",
		"group": "pitching",
		"season": season,
		"gameType": "R",
		"sportIds": 1,
	})
	splits = data["stats"][0]["splits"]
	return {s["team"]["name"]: s["stat"] for s in splits}


def fetch_team_performance(season: int = 2026, standings_type: str = "regularSeason") -> list[dict]:
	"""Fetch all MLB team standings and flatten into one list of team rows.

	Returns one entry per team (30 total in regular season) with league/division
	metadata, records, and rank/GB fields commonly needed for transforms.
	"""
	data = statsapi.get(
		"standings",
		{
			"leagueId": "103,104",  # AL + NL
			"season": season,
			"standingsTypes": standings_type,
			"hydrate": "team",
		},
	)

	rows: list[dict] = []
	for division_record in data.get("records", []):
		league = division_record.get("league", {})
		division = division_record.get("division", {})

		for team_record in division_record.get("teamRecords", []):
			team = team_record.get("team", {})
			team_league = team.get("league", {})
			team_division = team.get("division", {})
			league_id = league.get("id") or team_league.get("id")
			league_name = league.get("name") or team_league.get("name")
			division_name = division.get("name") or team_division.get("name")
			split_records = team_record.get("records", {}).get("splitRecords", [])
			last_ten_record = next((s for s in split_records if s.get("type") == "lastTen"), {})
			last_ten = None
			if last_ten_record:
				wins = last_ten_record.get("wins")
				losses = last_ten_record.get("losses")
				if wins is not None and losses is not None:
					last_ten = f"{wins}-{losses}"
				else:
					last_ten = last_ten_record.get("summary")

			rows.append(
				{
					"season": season,
					"league_id": league_id,
					"league_name": league_name,
					"division_id": division.get("id"),
					"division_name": division_name,
					"team_id": team.get("id"),
					"team_name": team.get("name"),
					"wins": team_record.get("wins", 0),
					"losses": team_record.get("losses", 0),
					"pct": team_record.get("winningPercentage"),
					"runs_scored": team_record.get("runsScored"),
					"runs_allowed": team_record.get("runsAllowed"),
					"run_differential": team_record.get("runDifferential"),
					"division_rank": team_record.get("divisionRank"),
					"league_rank": team_record.get("leagueRank"),
					"sport_rank": team_record.get("sportRank"),
					"wild_card_rank": team_record.get("wildCardRank"),
					"division_games_back": team_record.get("divisionGamesBack"),
					"league_games_back": team_record.get("leagueGamesBack"),
					"sport_games_back": team_record.get("sportGamesBack"),
					"wild_card_games_back": team_record.get("wildCardGamesBack"),
					"streak": (team_record.get("streak") or {}).get("streakCode"),
					"last_ten": last_ten,
					"elimination_number": team_record.get("eliminationNumber"),
					"wild_card_elimination_number": team_record.get("wildCardEliminationNumber"),
					"clinch_indicator": team_record.get("clinchIndicator"),
				}
			)

	rows.sort(
		key=lambda r: (
			r.get("league_name") or "",
			r.get("division_name") or "",
			r.get("division_rank") if r.get("division_rank") is not None else 999,
		)
	)
	return rows

if __name__ == "__main__":
    import json

    standings = fetch_team_performance()
    print(json.dumps(standings, indent=2))