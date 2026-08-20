from ..api.team_performance import fetch_team_performance
from ..api.player_stats import fetch_hitter_stats, fetch_pitcher_stats
from .managers import generate_manager_list


def generate_team_profile(season: int = 2026, standings_type: str = "regularSeason") -> list[dict]:
	"""Return team standings with aggregated batting/pitching stats and MLB/league ranks."""
	rows = fetch_team_performance(season=season, standings_type=standings_type)
	hitters = fetch_hitter_stats(season, player_pool='ALL')
	pitchers = fetch_pitcher_stats(season, player_pool='ALL')
	managers = generate_manager_list(season=season)
	manager_by_team = {m.get('team'): m.get('name') for m in managers if m.get('team') and m.get('name')}

	# Build team batting aggregates
	team_hitting = {}
	for p in hitters:
		tn = p.get('team', {}).get('name')
		if not tn:
			continue
		if tn not in team_hitting:
			team_hitting[tn] = {
				'hits': 0,
				'abs': 0,
				'hrs': 0,
				'walks': 0,
				'hbp': 0,
				'sf': 0,
				'total_bases': 0,
				'strikeouts': 0,
				'gidp': 0,
			}
		team_hitting[tn]['hits']        += float(p['stat'].get('hits') or 0)
		team_hitting[tn]['abs']         += float(p['stat'].get('atBats') or 0)
		team_hitting[tn]['hrs']         += float(p['stat'].get('homeRuns') or 0)
		team_hitting[tn]['walks']       += float(p['stat'].get('baseOnBalls') or 0)
		team_hitting[tn]['hbp']         += float(p['stat'].get('hitByPitch') or 0)
		team_hitting[tn]['sf']          += float(p['stat'].get('sacFlies') or 0)
		team_hitting[tn]['total_bases'] += float(p['stat'].get('totalBases') or 0)
		team_hitting[tn]['strikeouts']  += float(p['stat'].get('strikeOuts') or 0)
		team_hitting[tn]['gidp']        += float(p['stat'].get('groundIntoDoublePlay') or 0)

	# Build team pitching aggregates
	team_pitching = {}
	for p in pitchers:
		if p.get('position', {}).get('abbreviation') != 'P':
			continue
		tn = p.get('team', {}).get('name')
		if not tn:
			continue
		if tn not in team_pitching:
			team_pitching[tn] = {
				'outs': 0,
				'earned_runs': 0,
				'walks': 0,
				'intentional_walks': 0,
				'hits': 0,
				'ks': 0,
				'home_runs_allowed': 0,
				'hbp': 0,
				'blown_saves': 0,
			}
		ip = p['stat'].get('inningsPitched')
		if ip not in (None, ""):
			ip_text = str(ip)
			if "." not in ip_text:
				team_pitching[tn]['outs'] += int(float(ip_text)) * 3
			else:
				whole, frac = ip_text.split(".", 1)
				team_pitching[tn]['outs'] += int(float(whole)) * 3
				if frac.startswith("1"): team_pitching[tn]['outs'] += 1
				elif frac.startswith("2"): team_pitching[tn]['outs'] += 2
		team_pitching[tn]['earned_runs'] += float(p['stat'].get('earnedRuns') or 0)
		team_pitching[tn]['walks']       += float(p['stat'].get('baseOnBalls') or 0)
		team_pitching[tn]['intentional_walks'] += float(p['stat'].get('intentionalWalks') or 0)
		team_pitching[tn]['hits']        += float(p['stat'].get('hits') or 0)
		team_pitching[tn]['ks']          += float(p['stat'].get('pitchingStrikeOuts') or 0)
		team_pitching[tn]['home_runs_allowed'] += float(p['stat'].get('homeRuns') or 0)
		team_pitching[tn]['hbp']               += float(p['stat'].get('hitBatsmen') or 0)
		team_pitching[tn]['blown_saves']       += float(p['stat'].get('blownSaves') or 0)

	profiles = [
		{
			"league_name": r.get("league_name"),
			"division_name": r.get("division_name"),
			"team_id": r.get("team_id"),
			"team_name": r.get("team_name"),
			"manager": manager_by_team.get(r.get("team_name")),
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