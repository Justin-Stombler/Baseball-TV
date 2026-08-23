from ..api.team_performance import fetch_team_performance, fetch_team_hitting_stats, fetch_team_pitching_stats


def generate_team_profile(season: int = 2026, standings_type: str = "regularSeason") -> list[dict]:
	"""Return team standings with aggregated batting/pitching stats and MLB/league ranks."""
	rows = fetch_team_performance(season=season, standings_type=standings_type)
	team_hitting_stats = fetch_team_hitting_stats(season)
	team_pitching_stats = fetch_team_pitching_stats(season)

	def _to_float(value) -> float:
		try:
			return float(value)
		except (TypeError, ValueError):
			return 0.0

	# Build team batting aggregates from official team-level season totals.
	# This credits a traded player's stats to whichever team he earned them
	# with, rather than lumping his whole season onto his current roster team.
	team_hitting = {}
	for tn, stat in team_hitting_stats.items():
		team_hitting[tn] = {
			'hits': _to_float(stat.get('hits')),
			'abs': _to_float(stat.get('atBats')),
			'hrs': _to_float(stat.get('homeRuns')),
			'walks': _to_float(stat.get('baseOnBalls')),
			'hbp': _to_float(stat.get('hitByPitch')),
			'sf': _to_float(stat.get('sacFlies')),
			'total_bases': _to_float(stat.get('totalBases')),
			'strikeouts': _to_float(stat.get('strikeOuts')),
			'gidp': _to_float(stat.get('groundIntoDoublePlay')),
		}

	# Build team pitching aggregates from official team-level season totals.
	team_pitching = {}
	for tn, stat in team_pitching_stats.items():
		team_pitching[tn] = {
			'outs': _to_float(stat.get('outs')),
			'earned_runs': _to_float(stat.get('earnedRuns')),
			'walks': _to_float(stat.get('baseOnBalls')),
			'intentional_walks': _to_float(stat.get('intentionalWalks')),
			'hits': _to_float(stat.get('hits')),
			'ks': _to_float(stat.get('strikeOuts')),
			'home_runs_allowed': _to_float(stat.get('homeRuns')),
			'hbp': _to_float(stat.get('hitBatsmen')),
			'blown_saves': _to_float(stat.get('blownSaves')),
		}


	profiles = [
		{
			"league_name": r.get("league_name"),
			"division_name": r.get("division_name"),
			"team_id": r.get("team_id"),
			"team_name": r.get("team_name"),
			"wins": r.get("wins"),
			"losses": r.get("losses"),
			"pct": r.get("pct"),
			"runs_scored": r.get("runs_scored"),
			"runs_allowed": r.get("runs_allowed"),
			"run_differential": r.get("run_differential"),
			"division_rank": r.get("division_rank"),
			"wild_card_rank": r.get("wild_card_rank"),
			"division_games_back": r.get("division_games_back"),
			"wild_card_games_back": r.get("wild_card_games_back"),
			"streak": r.get("streak"),
			"last_ten": r.get("last_ten"),
			"team_avg": round(h['hits'] / h['abs'], 3) if h.get('abs', 0) > 0 else 0,
			"team_ops": round(
				((h['hits'] + h['walks'] + h['hbp']) / (h['abs'] + h['walks'] + h['hbp'] + h['sf'])
				 if (h.get('abs', 0) + h.get('walks', 0) + h.get('hbp', 0) + h.get('sf', 0)) > 0 else 0)
				+ (h['total_bases'] / h['abs'] if h.get('abs', 0) > 0 else 0), 3),
			"team_home_runs": int(h.get('hrs', 0)),
			"team_walks": int(h.get('walks', 0)),
			"team_batting_strikeouts": int(h.get('strikeouts', 0)),
			"team_gidp": int(h.get('gidp', 0)),
			"team_total_bases": int(h.get('total_bases', 0)),
			"team_era": round((pi['earned_runs'] * 9) / (pi['outs'] / 3), 2) if pi.get('outs', 0) > 0 else 0,
			"team_whip": round((pi['walks'] + pi['hits']) / (pi['outs'] / 3), 2) if pi.get('outs', 0) > 0 else 0,
			"team_strikeouts": int(pi.get('ks', 0)),
			"team_pitching_walks": int(pi.get('walks', 0)),
			"team_home_runs_allowed": int(pi.get('home_runs_allowed', 0)),
			"team_blown_saves": int(pi.get('blown_saves', 0)),
			"team_fip": round(
				((13 * pi.get('home_runs_allowed', 0)) + (3 * ((pi.get('walks', 0) + pi.get('intentional_walks', 0)) + pi.get('hbp', 0))) - (2 * pi.get('ks', 0)))
				/ (pi.get('outs', 0) / 3) + 3.1,
				2, ##done using Fangraphs calculations and their FIP constant of 3.1 for 2026
			) if pi.get('outs', 0) > 0 else 0,
		}
		for r in rows
		for h in [team_hitting.get(r.get("team_name"), {})]
		for pi in [team_pitching.get(r.get("team_name"), {})]
	]

	# Add MLB-wide and league-specific ranks for all numerical stats
	for stat_key, higher_is_better in {
		"runs_scored": True, "runs_allowed": False, "run_differential": True,
		"team_avg": True, "team_ops": True, "team_home_runs": True,
		"team_walks": True, "team_batting_strikeouts": False, "team_gidp": False, "team_total_bases": True,
		"team_era": False, "team_whip": False, "team_strikeouts": True,
		"team_pitching_walks": False, "team_home_runs_allowed": False, "team_blown_saves": False, "team_fip": False,
	}.items():
		sorted_all = sorted(profiles, key=lambda p: float(p.get(stat_key) or 0), reverse=higher_is_better)
		for rank, profile in enumerate(sorted_all, start=1):
			profile[f"{stat_key}_rank"] = rank

		for lg in ["American League", "National League"]:
			sorted_lg = sorted([p for p in profiles if p.get("league_name") == lg],
				key=lambda p: float(p.get(stat_key) or 0), reverse=higher_is_better)
			for lg_rank, profile in enumerate(sorted_lg, start=1):
				profile[f"{stat_key}_league_rank"] = lg_rank

	return profiles


if __name__ == "__main__":
	import json
	print(json.dumps(generate_team_profile(), indent=2))