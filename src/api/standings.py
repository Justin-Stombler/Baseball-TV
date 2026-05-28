##pulls all available standings
##transform will pull current this season by division
##render will build

import statsapi

def get_standings_data(date: int = None, league: str = None) -> list:
    """Get MLB standings for a given season and league."""
    season = statsapi.latest_season()
    if league not in ['AL', 'NL', None]:
        raise ValueError("League must be 'AL', 'NL', or None")

    standings = statsapi.standings_data(season=season)
    
    if league:
        standings = [s for s in standings if s['league'] == league]

    return standings

if __name__ == "__main__":
    standings = get_standings_data()
    print(type(standings))