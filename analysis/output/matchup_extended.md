# Meta Evolution Across Builds and Uncertainty of the Cyclic Share

Builds with >= 10,000 matches, Pre-Season 2016.

## Corrected cyclic share, overall (bootstrap over matches)

- Point estimate: **5.1%**
- 95% CI (12 replicates): [3.6%, 7.7%]

## Rating stability between consecutive builds

| From | To | Rating Spearman | Cyclic-residual Pearson |
|---|---|---|---|
| 5.22.0.297 | 5.22.0.301 | 0.6969 | -0.0022 |
| 5.22.0.301 | 5.23.0.239 | 0.6046 | -0.0093 |
| 5.23.0.239 | 5.23.0.250 | 0.6903 | -0.0064 |
| 5.23.0.250 | 5.24.0.254 | 0.6417 | -0.0091 |
| 5.24.0.254 | 5.24.0.256 | 0.7717 | -0.0091 |
| 5.24.0.256 | 5.24.0.259 | 0.7748 | 0.015 |

## Biggest rating movers per build boundary

### 5.22.0.297 -> 5.22.0.301

- Gainers: Urgot (+0.3442), Zilean (+0.3197), Kog'Maw (+0.2298), Talon (+0.2272), Fiora (+0.2234)
- Losers: Tryndamere (-0.3245), Fiddlesticks (-0.3052), Vel'Koz (-0.2036), Evelynn (-0.199), Corki (-0.1964)

### 5.22.0.301 -> 5.23.0.239

- Gainers: Urgot (+0.4359), Mordekaiser (+0.419), Evelynn (+0.2269), Gnar (+0.2077), Fiddlesticks (+0.1829)
- Losers: Karthus (-0.242), Xin Zhao (-0.2395), Singed (-0.2357), Zilean (-0.1916), Lucian (-0.1859)

### 5.23.0.239 -> 5.23.0.250

- Gainers: Zyra (+0.2447), Corki (+0.223), Malzahar (+0.2187), Poppy (+0.1935), Akali (+0.1814)
- Losers: Mordekaiser (-0.2966), Urgot (-0.2759), Twitch (-0.2112), Karma (-0.1695), Nunu (-0.1616)

### 5.23.0.250 -> 5.24.0.254

- Gainers: Cassiopeia (+0.2608), Sivir (+0.2099), Riven (+0.2023), Katarina (+0.1667), Varus (+0.1522)
- Losers: Hecarim (-0.2549), Poppy (-0.2452), Galio (-0.2406), Rek'Sai (-0.1917), Shyvana (-0.1841)

### 5.24.0.254 -> 5.24.0.256

- Gainers: Poppy (+0.2196), Galio (+0.1563), Vi (+0.1466), Jayce (+0.1393), Talon (+0.1354)
- Losers: Cassiopeia (-0.2127), Mordekaiser (-0.2013), Viktor (-0.1676), Katarina (-0.14), Yorick (-0.1399)

### 5.24.0.256 -> 5.24.0.259

- Gainers: Mordekaiser (+0.2847), Karthus (+0.2745), Veigar (+0.1803), Vi (+0.1565), Kog'Maw (+0.1165)
- Losers: Nocturne (-0.1845), Zac (-0.1593), Fiddlesticks (-0.1547), Gragas (-0.1096), Aatrox (-0.1008)
