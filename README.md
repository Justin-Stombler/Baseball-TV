## Baseball-TV

Hi! I'm Justin, and I have been building this little Baseball TV as a personal project to both whet my ravenous appetite for baseball knowledge and show off my skills in repository and dataset setup and design. Back in 2020, I began learning Python and SQL during lockdown using baseball data as my main catalyst, and it quickly became an obsession. I pushed myself both technically and creatively, keeping a blog to this day at www.sevenyardsback.com. I was extremely fortuante to have these efforts pay off, as I began landing my first analyst roles. As I move onto the next chapter of my professional career and look to advance my skillset even further, this felt like a fantastic next opportunity.

Everything below is handwritten. Is that a pro? Is that a con? I'm not yet sure, but at least you know.

#### *Introduction*

Rotating Baseball Stat Visaulization Host, currently optimized for 240x240 screens.

Photos upload to screen's device via API and delete themselves upon upload of the next round, order is controlled via the carousel order in main.py.

In general, this project has been put together for three reasons:

1) I love Baseball and data, and this seemed like a tremendously fun way to tie those together
2) Baseball and data have continued to be a very powerful learning tool for me, and I wanted to build this repository to show off the things I have learned in my professional career in data, as I seek similar roles in the future
3) I genuinely think this is a cool idea, and would be kicking myself if I didn't try to build it

#### *Workflow and Design*

While this pipeline does not output into a source system, so to say, this is still very much written with my knowledge of both ETL and DataVault concepts in mind.

There are 3 distinct layers at play here.

1. The 'raw' data, called via the statsapi library wrapper for the MLB's official API, and the pybasell library for Baseball Savant metrics. Here, data is returned in a Json structure for information in the current season for any batting, pitchig, biographic, roster, or game state information I am intersted in.
2. The 'transform' layer. The preceding Jsons are then stripped of data I didn't feel was necessary for the visualization and/or cleaned as required. These will also pull in from the static data folder to add a player's jersey numbers and team abbreviations, so the render layer can keep use those dynamically.
3. The 'render' layer, which isn't really a layer at all. These are merely functions that contain shapes drawn with the Pillow Python Image Library (PIL), combined with dynamically called data from the transform layer are required. These functions, when called in main.py, populate with data and create the images displayed on the screen one by one using push.py. These are then deleted after being shown, to prevent the device from overflowing (only holds 2MB roughly).

The images themselves and the various details they can show are largely controlled in the config files.

One, the display config file, sets the order of the carousel, including

- How many seconds a screen should show for
- How many times a mode should iterate before moving onto the next
- How to handle playoff games v. regular season box scores

The second, the stat config file, contains a wide variety of information about how the stats are meant to be displayed including:

- Is a stat meant to be ascending or descending?
- Should a specific stat be available for leaderboard creation? Not every stat makes for a compelling leaderboard.
- If a stat is meant to be attributed to a hitter or a pitcher
- Is the stat aggregated by sum? By rate? This was a hyper-critical step in data assurance.
- The stats to be shown and the order for the recent apperances and player bio modes.

The config files are very poweful, and allow me to pick and choose stats and display parameters much more quickly than having to edit the transforms code itself. The hope is that if this were a released product, these files would serve as the basis for a settings menu that a user would have to edit the visualizations on their own Baseball TV.

Lastly, although the data displayed is ordered formulacially, the images themselves are created randomly from the appropriate bucket of players, teams, or stats to allow for an experience where you are never seeing the same thing in the order. I wanted to mimic the feeling of flipping through channels.

#### *Modes*

As of this writing, the Baseball TV supports 12 various kinds of images. All created dynamically with live data, updating in real-time when the image is created.

1. Traditional Player Stats
2. Statcast Data
3. Batted Ball Profiles
4. Player Biographies
5. Player's Recent Performances
6. Pitch Arsenals (PITCHER ONLY)
7. League Leaderboards
8. Team Leaderboards
9. Division Standings
10. Wildcard Standings
11. Team Profiles
12. Live Box Scoers

#### *Baseball Specific Minutae*

One of the most gratifying parts of this project was that it turned into an attempt to reverse engineer a highly accurate and easily comprehensive baseball database.

As such, a non-exhaustive list of just some of the considerations I've put into this program are below:

- Upon startup, the program always pulls updated rosters, and ensure only players who are on an active MLB roster are able to show up. This does mean players on the IL are not available in the pool, but that was an intentional design choice. This does mean that trades and call-ups are caught in real-time.
- Additionally, only players who are actually qualified for league leaderboards are able to show up on the league leaderboards. However, for team-specific leaderboards the Baseball Savant approach was taken, where a picher must have 1.25 innings per games played, and a batter 2.1 at bats. This allows the lesser konwn players on a team (especially relievers) to be able to appear in images.
- I came up with my own suite of pitch abbreviations and color choices for the pitch arsenal screen, which took me back to my days playing MVP Baseball 05.
- There is a file that pulls in the hex colors of each team, and their primary and secondary colors always make an apperance in the player-specific screen to match the team they play for.
- FIP is not available via either of the APIs I have used, but I wanted it for the Team Profiles. So I pulled the Fangraphs formula and reverse engineered the 2026 constant to ensure my hand-calculated FIP always matches that reported elsewhere.
- The player bio screen is a direct homage to the baseball cards of my youth, hence the traditional counting stats and biographical information. It is also designed intentionally to mimic a baseball card.
- Live Box Scores had to be designed to handle any number of cases, including extra innings, rainouts, and teams who don't list probable starters. Additonally, a * was added so the viewer knows that a half inning is current live.
- X and Y data for pitch location had to be averaged, but also normalized so I could make sure it fit the image of the to-scale strikezone I created.
- The batted ball profile uses colored cones set to the exact angles for each hit type as described by MLB's statistics glossary.

#### *See Me Live!*

Using the link below, you can access a Youtube Video designed to help you get a sense of both the scale of the project, and its functionalities.

[youtu.be/U9X71sG-Pi0](https://youtu.be/U9X71sG-Pi0)

#### *Album*

<img src="docs/images/album/IMG_9233.jpg" alt="Baseball TV photo 1" width="45%">
<img src="docs/images/album/IMG_9236.jpg" alt="Baseball TV photo 2" width="45%">
<img src="docs/images/album/IMG_9238.jpg" alt="Baseball TV photo 3" width="45%">
<img src="docs/images/album/IMG_9239.jpg" alt="Baseball TV photo 4" width="45%">
<img src="docs/images/album/IMG_9240.jpg" alt="Baseball TV photo 5" width="45%">
<img src="docs/images/album/IMG_9241.jpg" alt="Baseball TV photo 6" width="45%">
<img src="docs/images/album/IMG_9242.jpg" alt="Baseball TV photo 7" width="45%">
<img src="docs/images/album/IMG_9248.jpg" alt="Baseball TV photo 8" width="45%">
