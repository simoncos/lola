# LoLA

LoLA is a LoL (League of Legends) game data analysis / analytics project. See [report](/report).

## Crawling

The data crawling part is based on [Riot API](https://developer.riotgames.com/api-methods/) and a Python wrapper [Cassiopeia](https://github.com/meraki-analytics/cassiopeia) (There is a In-Memory cache problem in Cass, refer to [here](https://github.com/meraki-analytics/cassiopeia/issues/40)). A SQLite database is designed and used in this project, which remodels and stores game objects for our analysis objectives. The database I/O part involves [sqlite3](https://docs.python.org/3.5/library/sqlite3.html) and [pandas](http://pandas.pydata.org/). 

This part has been well tested with `Python 3.5`, though in some environments (e.g. `Windows cmd`) a `decode`/`encode` error may occur in `print` functions due to multi-language issue; you can just comment out all `print` codes without any influcence on crawling itself. `Python 2.X` may also run well with a few edits.

We have obtained data of over 220,000 `Ranked-SOLO-5x5` matches with details in the North American region, Pre-Season 2016.

## Analysis

We are doing analyses such as:

- Champion Rank
- Champion Clustering
- Champion Recommendation
- Match Prediction
- Cheating Detection

Our results will be uploaded continuously. As we are doing many experiments, code in this part is quite messy now and will be refined later.

If you are interested in this project or have any problem, feel free to participate in.

## Dataset

- [Google Drive](https://drive.google.com/file/d/1X9B60eUSWarMEG9RS3JHbWDaeNuB48LF/view?usp=sharing)
