# P1: Selection-Confound-Controlled Skill Expression (prototype)

Skill amplification = weighted slope of a player's on-champion performance
vs their leave-one-out baseline on all other champions. Conditions on each
player's revealed skill instead of tier, so it is robust to the cross-tier
selection confound in P0.

Config: players with >= 15 games, cells with >= 3 games, champions with >= 80 players. 123 champions scored.

## Correlation with P0 tier-slope ranking

- amp_slope_win_vs_P0_tier_slope_spearman: 0.043
- amp_slope_lane_diff_vs_P0_tier_slope_spearman: -0.0136
- n_champions_compared: 123

## Top 10 skill amplifiers (lane-dominance metric)

| Champion | amp slope (lane) | amp slope (win) | players |
|---|---|---|---|
| Lissandra | +0.868 | +0.142 | 279 |
| Viktor | +0.780 | -0.033 | 430 |
| Rek'Sai | +0.773 | -0.073 | 458 |
| Nunu | +0.727 | +0.036 | 119 |
| Nidalee | +0.669 | +0.126 | 608 |
| Jax | +0.640 | +0.018 | 864 |
| Elise | +0.632 | -0.093 | 490 |
| Hecarim | +0.630 | +0.006 | 411 |
| Azir | +0.616 | +0.050 | 312 |
| Cho'Gath | +0.612 | -0.098 | 272 |

## Bottom 10 (least skill-amplifying)

| Champion | amp slope (lane) | amp slope (win) | players |
|---|---|---|---|
| Soraka | +0.062 | +0.014 | 665 |
| Xin Zhao | +0.051 | -0.281 | 514 |
| Karma | +0.049 | -0.241 | 262 |
| Jayce | +0.049 | +0.028 | 205 |
| Varus | +0.034 | -0.033 | 173 |
| Karthus | +0.019 | +0.152 | 94 |
| Draven | +0.008 | -0.006 | 423 |
| Leona | -0.015 | -0.055 | 568 |
| Aatrox | -0.022 | +0.008 | 121 |
| Gragas | -0.033 | -0.146 | 192 |
