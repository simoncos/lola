# Counter-Structure Decomposition of the Champion Kill Matrix (prototype)

Source: `results/kill_matrix_22k.csv` — 128 champions, 12,663,291 kill events (full-crawl derived matrix).

Method: pairwise kill-exchange log-odds -> weighted HodgeRank decomposition into a transitive rating (least-squares Elo, cf. mElo/Nash averaging, Balduzzi et al. 2018) plus a cyclic (rock-paper-scissors) residual.

## Headline numbers

- **Transitive share of pairwise structure: 92.4%**
- **Cyclic (counter-pick) share: 7.6%**
- Spearman correlation of the modern rating vs the 2016 eigenvector-centrality ranking: 0.040

Interpretation: the near-zero correlation with the 2016 ranking is itself a finding - eigenvector centrality on the row-normalized kill matrix largely tracks kill *volume* (popularity x aggression), whereas the HodgeRank rating measures pairwise kill *dominance* conditioned on interactions. The two methods answer different questions; the 2016 report's 'no significant difference from average score' observation is consistent with this.

## Top 15 champions by transitive kill-dominance rating

| # | Champion | Rating (log-odds) |
|---|---|---|
| 1 | LeBlanc | 0.454 |
| 2 | Zed | 0.440 |
| 3 | Fizz | 0.391 |
| 4 | Anivia | 0.377 |
| 5 | Talon | 0.373 |
| 6 | Kassadin | 0.369 |
| 7 | Rengar | 0.364 |
| 8 | Shaco | 0.350 |
| 9 | Nocturne | 0.340 |
| 10 | Tristana | 0.336 |
| 11 | Katarina | 0.333 |
| 12 | Twitch | 0.319 |
| 13 | Evelynn | 0.318 |
| 14 | Wukong | 0.311 |
| 15 | Garen | 0.311 |

## Strongest cyclic triads (rock-paper-scissors)

| Cycle | Strength (log-odds) | Min pair interactions |
|---|---|---|
| Talon > Vel'Koz > Taric > Talon | 1.496 | 214 |
| Janna > Tryndamere > Ziggs > Janna | 1.461 | 264 |
| Cho'Gath > Taric > Tryndamere > Cho'Gath | 1.447 | 266 |
| Azir > Taric > Talon > Azir | 1.445 | 244 |
| Azir > Taric > Rengar > Azir | 1.441 | 244 |
| Janna > Tryndamere > Orianna > Janna | 1.428 | 643 |
| Lux > Taric > Rengar > Lux | 1.404 | 669 |
| Cho'Gath > Taric > Fiora > Cho'Gath | 1.382 | 266 |
| Rengar > Vel'Koz > Taric > Rengar | 1.356 | 214 |
| Gangplank > Janna > Tryndamere > Gangplank | 1.354 | 665 |
| Talon > Veigar > Taric > Talon | 1.342 | 229 |
| Aatrox > Rumble > Sona > Aatrox | 1.328 | 224 |
| Orianna > Taric > Tryndamere > Orianna | 1.327 | 216 |
| Braum > Tryndamere > Gangplank > Braum | 1.323 | 882 |
| Ahri > Taric > Talon > Ahri | 1.319 | 288 |

## Strongest pairwise counter relationships (cyclic residual)

| Relationship | Cyclic log-odds | Interactions |
|---|---|---|
| Ziggs beats Janna | 0.734 | 264 |
| Azir beats Taric | 0.7 | 244 |
| Zilean beats Illaoi | 0.688 | 228 |
| Taric beats Tryndamere | 0.673 | 532 |
| Cho'Gath beats Taric | 0.667 | 266 |
| Galio beats Annie | 0.626 | 385 |
| Orianna beats Janna | 0.617 | 643 |
| Veigar beats Janna | 0.61 | 504 |
| Janna beats Tryndamere | 0.603 | 665 |
| Taric beats Rengar | 0.601 | 806 |
| Galio beats Teemo | 0.6 | 216 |
| Vel'Koz beats Taric | 0.597 | 214 |
| Rumble beats Sona | 0.595 | 248 |
| Gangplank beats Braum | 0.572 | 882 |
| Taric beats Talon | 0.562 | 288 |

## Caveats (prototype)

- Kill exchanges are a *proxy* for matchup dominance; the paper-grade version uses per-match win/loss matchup matrices sliced by patch and tier (requires full lola.db).
- Kills reflect aggression profiles (assassins kill more than tanks regardless of matchup advantage); the transitive rating is therefore a 'kill-dominance' rating, not a strength rating. The win-based matrix removes this bias.
- No patch/tier slicing yet - this aggregates patches 5.21-6.1 and all tiers.
