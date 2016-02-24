# lola
LOL (League of Legends) game data analysis / analytics project.

The data crawling part is based on [Riot API](https://developer.riotgames.com/api/methods) and a Python wrapper [Cassiopeia](https://github.com/meraki-analytics/cassiopeia).

A SQLite database is used in this project, which extracts and remodels game objects for our analysis objectives. The I/O part involves sqlite3 and [pandas](http://pandas.pydata.org/).