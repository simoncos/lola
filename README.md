# Intro

This is a LOL (League of Legends) game data analysis / analytics project.

# Crawling

The data crawling part is based on [Riot API](https://developer.riotgames.com/api/methods) and a Python wrapper [Cassiopeia](https://github.com/meraki-analytics/cassiopeia). A SQLite database is used in this project, which extracts and remodels game objects for our analysis objectives. The I/O part involves [sqlite3](https://docs.python.org/3.5/library/sqlite3.html) and [pandas](http://pandas.pydata.org/). 

This part has been well tested with Python 3.5, though in some environments (e.g. Windows CMD) trivial errors (e.g. decode/encode problem in printing; you can just comment out all printing codes without any influcence on crawling). Python 2.X may also run well without too many edits (we cannot 100% guarantee this). In addition, because both `Riot API` and `Cassiopeia` are not stable for now, we may also update constantly to be compatible.

# Dataset

For now we have obtained data of over 32,000 Ranked-SOLO-5x5 matches with details and over 15,000 summoners (LOL gamers) in the North American region, Pre-Season 2016. And we plan to swallow much more.

# Analysis

We intend to do analyses such as:

- Champion Ability Rank
- Champion Clustering
- Champion Recommendation
- Wining Analysis 
- Match Prediction
- Cheating Detection

If you are interested in this project, feel free to participate in.