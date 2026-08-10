# LoLA

LoLA is a historical League of Legends data-analysis project. The committed
[project reports](report/) describe the 2016 course project and its results;
they are not evidence that the current checkout can reproduce those results.

## Repository status

The default branch is an archival legacy baseline. It has no locked dependency
environment or CI workflow, and it has not been validated against current Riot
APIs or current Cassiopeia releases.

| Area | Current default-branch status |
| --- | --- |
| Crawling | Legacy single-seed crawler; not an implementation of the reports' three-seed 100k/60k/60k stopping protocol |
| Matrix/preprocessing | Implemented; synthetic SQLite tests cover event identity, idempotent preprocessing, and pick normalization |
| Clustering | Legacy prototype; requires the historical scientific-Python stack and a compatible database |
| Match prediction | Historical/report prototype; `match_predict.py` does not reproduce the reports' 220k/31-feature or six-cluster experiments |
| Cheating detection | Listed as a historical objective, but not implemented in this tree |

The files under `results/` and `report/` are historical artifacts without a
committed source-data fingerprint, run manifest, or environment lock. Do not
treat them as a fresh reproduction or current academic validation.

## Crawling

The crawler was built around the Riot API and the historical
[Cassiopeia](https://github.com/meraki-analytics/cassiopeia) wrapper. Before a
legacy run, initialize an empty database explicitly:

```sh
sqlite3 lola.db < sqlite_schema.sql
```

Provide the API key outside the repository:

```sh
export LOLA_RIOT_API_KEY=your-key
python3 data_crawl.py
```

`LOLA_REGION`, `LOLA_SEED_SUMMONER_ID`, `LOLA_SEASON`, and
`LOLA_RANKED_QUEUE` can override the historical defaults. This entry point runs
one seed. Multi-seed orchestration, stopping thresholds, database merging, API
compatibility, and retry recovery still require separate operator validation.

## Dataset and distribution boundary

The project reports state that the original team collected more than 220,000
North American `Ranked-SOLO-5x5` matches from Pre-Season 2016. A historical
copy was linked on [Google Drive](https://drive.google.com/file/d/1X9B60eUSWarMEG9RS3JHbWDaeNuB48LF/view?usp=sharing).

The current default branch does not include a data card, checksum/manifest,
license, permission record, or privacy review. The schema includes summoner IDs
and names. Verify provenance, Riot terms, redistribution permission, and
identity handling before downloading, using, or republishing that dataset.

## Analysis and tests

The legacy tree contains champion ranking, relationship matrices, clustering,
recommendation experiments, and a match-prediction prototype. The narrow test
suite uses only generated SQLite fixtures:

```sh
python3 -m unittest discover -s tests -v
```

Passing these tests validates the covered code contracts only. It does not
validate the historical dataset, report figures, model quality, licensing, or
real-data reproducibility.
