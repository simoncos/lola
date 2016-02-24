# Intro

This is a LOL (League of Legends) game data analysis / analytics project.

The data crawling part is based on [Riot API](https://developer.riotgames.com/api/methods) and a Python wrapper [Cassiopeia](https://github.com/meraki-analytics/cassiopeia). A SQLite database is used in this project, which extracts and remodels game objects for our analysis objectives. The I/O part involves sqlite3 and [pandas](http://pandas.pydata.org/). 

For now we have obtained data of over 20,000 Ranked-SOLO-5x5 match with details and over 8,000 summoners (LOL gamers) in North American region, Pre-Season 2016. And we plan to swallow much more.

# Analysis

We intend to do analyses such as:

- Champion Ability Rank
- Champion Clustering
- Champion Recommendation
- Wining Analysis 
- Match Prediction
- Cheating Detection

If you are interested in this project, feel free to participate in.