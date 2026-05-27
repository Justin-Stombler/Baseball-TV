###1. Transform player data into aggregated top 10 lists by the whatever statistics desired
###2. Will require AL/NL split (it's in api.players)
###3. Leave option to filter for only qualfied players

from ..api.players import fetch_hitter_stats, fetch_pitcher_stats
from data.team_abbreviations import get_team_abbreviation
import json

def hitter_leaderboards(season: int = 2026, qualified_only: bool = True) -> list[dict]:
    """Get top 5 hitters for predefined leaderboard stats."""

    relevant_stats = [['runs', 'doubles', 'triples', 'homeRuns', 'avg', 'ops']]

    player_pool = 'QUALIFIED' if qualified_only else 'ALL'
    splits = fetch_hitter_stats(season, player_pool=player_pool)

    # Ad-hoc test: print all unique stat names from the hitter JSON payload.
    for p in splits:
        for stat_name in p.get('stat', {}).keys():
            if stat_name in relevant_stats:
                leaderboard = sorted(splits, key=lambda x: x['stat'].get({stat_name}, 0), reverse=True)[:5]
    
                ##return only player and average for simplicity
                # leaderboard = [ ##returning dict because render is set up to receive
                #     {
                #         'league' : p['league']['name'],
                #         'name': p['player']['fullName'],
                #         stat_name: p['stat'].get(stat_name),
                #         'team': get_team_abbreviation(p['team']['name'])
                #     }
                #     for p in leaderboard
                # ]
                return leaderboard

##GOAL IS FUNCTION THAT RETURNS DICT OF TOP 5 BASED ON LEAGUE AND STAT
##CAN END WITH GENERATE LEADERBOARD FUNCTION
##THAT CAN THEN BE GIVEN TO RENDER AND TEXT WILL BE LEFT BASED ON 
##POSITION IN LEADERBOARD AND LEAGUE
##THEN IN MAIN THE LEAGUE AND STAT CAN BE RANDOMLY CHOSEN FOR VARIETY FOR NOW

if __name__ == "__main__":
    top_averages = hitter_leaderboards()
    print(top_averages)