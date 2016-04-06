# LoLA

LoLA is a LoL (League of Legends) game data analysis / analytics project.

## Crawling

The data crawling part is based on [Riot API](https://developer.riotgames.com/api/methods) and a Python wrapper [Cassiopeia](https://github.com/meraki-analytics/cassiopeia). A SQLite database is designed and used in this project, which remodels and stores game objects for our analysis objectives. The database I/O part involves [sqlite3](https://docs.python.org/3.5/library/sqlite3.html) and [pandas](http://pandas.pydata.org/). 

This part has been well tested with `Python 3.5`, though in some environments (e.g. `Windows cmd`) a `decode`/`encode` error may occur in `print` functions due to multi-language issue; you can just comment out all `print` codes without any influcence on crawling itself. `Python 2.X` may also run well with a few edits. In addition, since both `Riot API` and `Cassiopeia` are not quite stable for now, we may also update constantly to keep compatible.

We have obtained data of over 220,000 `Ranked-SOLO-5x5` matches with details in the North American region, Pre-Season 2016. And we plan to swallow more in the future.

## Analysis

We are doing analyses such as:

- Champion Ability Rank
- Champion Clustering
- Champion Recommendation
- Winning Analysis and Match Prediction
- Cheating Detection

Interesting results will be uploaded continuously. As we are doing many experiments, code in this part is quite messy now and will be refined later.

## Database

We plan to share our database file later.

If you are interested in this project, feel free to participate in.