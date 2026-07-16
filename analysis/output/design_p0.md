# P0: Skill Expression & Bans-as-Perceived-Power (prototype)

Real data, 222,652 matches. Win-based single metric; no confound correction yet (see PROPOSAL caveats).

## RQ1 — Champions that most reward mastery (win-rate slope vs tier)

| Champion | slope (WR per tier step) | WR low (Bronze/Silver) | WR high (Diamond+) |
|---|---|---|---|
| Nidalee | +0.0195 | 0.421 | 0.486 |
| Nunu | +0.0162 | 0.481 | 0.536 |
| Kindred | +0.0160 | 0.454 | 0.511 |
| Lulu | +0.0144 | 0.470 | 0.517 |
| Talon | +0.0123 | 0.499 | 0.538 |
| Rek'Sai | +0.0120 | 0.473 | 0.514 |
| Ryze | +0.0114 | 0.444 | 0.482 |
| Rengar | +0.0106 | 0.485 | 0.521 |
| Varus | +0.0104 | 0.489 | 0.521 |
| Maokai | +0.0104 | 0.455 | 0.486 |

### Champions that punish (or don't reward) skill — bottom 10

| Champion | slope | WR low | WR high |
|---|---|---|---|
| Nasus | -0.0095 | 0.529 | 0.495 |
| Tahm Kench | -0.0096 | 0.502 | 0.472 |
| Jax | -0.0101 | 0.512 | 0.478 |
| Brand | -0.0102 | 0.558 | 0.522 |
| Ekko | -0.0112 | 0.491 | 0.455 |
| Nocturne | -0.0123 | 0.528 | 0.481 |
| Warwick | -0.0136 | 0.520 | 0.447 |
| Amumu | -0.0172 | 0.550 | 0.490 |
| Illaoi | -0.0177 | 0.470 | 0.415 |
| Zyra | -0.0191 | 0.548 | 0.489 |

## RQ2 — Ban vs actual power quadrants

Counts: {'fair': 58, 'sleeper': 44, 'overpowered': 18, 'anti-fun': 8}

### Most 'anti-fun' (banned hard, not actually strong)

| Champion | ban rate | win rate | perceived−actual |
|---|---|---|---|
| Illaoi | 0.332 | 0.455 | +4.226 |
| Tahm Kench | 0.494 | 0.494 | +4.042 |
| Yasuo | 0.313 | 0.476 | +3.190 |
| Darius | 0.233 | 0.485 | +2.116 |
| Kindred | 0.200 | 0.490 | +1.631 |
| Poppy | 0.061 | 0.469 | +1.262 |
| Rengar | 0.171 | 0.495 | +1.136 |
| Vayne | 0.068 | 0.496 | +0.226 |

### Biggest 'sleepers' (strong, rarely banned)

| Champion | ban rate | win rate | perceived−actual |
|---|---|---|---|
| Vel'Koz | 0.001 | 0.525 | -1.586 |
| Nami | 0.001 | 0.525 | -1.605 |
| Udyr | 0.007 | 0.528 | -1.650 |
| Trundle | 0.044 | 0.535 | -1.650 |
| Talon | 0.007 | 0.529 | -1.710 |
| Sona | 0.003 | 0.529 | -1.757 |
| Volibear | 0.011 | 0.533 | -1.839 |
| Malzahar | 0.009 | 0.534 | -1.886 |
| Amumu | 0.006 | 0.534 | -1.943 |
| Janna | 0.004 | 0.542 | -2.279 |
