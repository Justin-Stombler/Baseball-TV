from api import fetch_hitter_stats
from api import fetch_pitcher_stats

##Firstly, checking out the data

if __name__ == "__main__":
    hitters = fetch_hitter_stats()
    pitchers = fetch_pitcher_stats()
    
    print(hitters[0])
    print(pitchers[0])