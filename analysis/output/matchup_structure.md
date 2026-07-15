# Win-Based Matchup Structure by Patch and Tier

Real match outcomes (25 blue-vs-red champion pairs per match), weighted
HodgeRank decomposition into transitive strength + cyclic counter residual.
Side advantage cancels by folding both orientations.

## Transitive vs cyclic structure by slice

Raw cyclic shares are sample-size artifacts: binomial noise is almost
entirely non-transitive and contributes near-constant energy per pair,
while signal energy grows with the number of games (a match-level
permutation null shows ~92% 'cyclic' share on pure noise). The
corrected column subtracts the permutation-null energies (3 perms)
from both components before forming the share.

| Slice | Matches | Cyclic (raw) | **Cyclic (corrected)** | Signal/noise | Rating Spearman vs overall |
|---|---|---|---|---|---|
| overall | 222,652 | 27.1% | **5.0%** | 2.942 | — |
| patch 5.22 | 41,355 | 52.3% | **4.2%** | 0.819 | 0.7834 |
| patch 5.23 | 51,992 | 54.0% | **3.6%** | 0.745 | 0.8982 |
| patch 5.24 | 127,999 | 35.1% | **4.4%** | 1.866 | 0.957 |
| tier low | 60,348 | 47.8% | **3.6%** | 1.027 | 0.9071 |
| tier mid | 115,453 | 38.1% | **6.0%** | 1.692 | 0.9789 |
| tier high | 43,939 | 58.1% | **4.8%** | 0.633 | 0.7737 |

## Top 10 champions by matchup strength (overall)

| # | Champion | Rating (log-odds) |
|---|---|---|
| 1 | Miss Fortune | 0.1961 |
| 2 | Janna | 0.1799 |
| 3 | Dr. Mundo | 0.1791 |
| 4 | Brand | 0.1707 |
| 5 | Trundle | 0.1559 |
| 6 | Amumu | 0.1523 |
| 7 | Rammus | 0.1509 |
| 8 | Malzahar | 0.1499 |
| 9 | Volibear | 0.1468 |
| 10 | Sona | 0.1316 |

## Strongest counter relationships (cyclic residual, overall)

| Relationship | Cyclic log-odds | Games |
|---|---|---|
| Olaf counters Darius | 0.346 | 367 |
| Kennen counters Renekton | 0.345 | 358 |
| Teemo counters Bard | 0.319 | 455 |
| Janna counters Rumble | 0.314 | 303 |
| Nami counters Vel'Koz | 0.312 | 346 |
| Zed counters Vel'Koz | 0.302 | 806 |
| Ryze counters Illaoi | 0.295 | 336 |
| Renekton counters Akali | 0.294 | 330 |
| Shyvana counters Shen | 0.285 | 461 |
| Corki counters Elise | 0.283 | 347 |
| Jax counters Xerath | 0.279 | 326 |
| Shen counters Twitch | 0.275 | 470 |

Notes: pairs reported only when the two champions met in >= 300 games. Patches 5.21 (8 matches) and 6.1 (1,298) excluded from per-patch slices for sample size.
