# Literature Review: Graph/Network Analysis, Game Balance, Datasets & Frontier Trends (2016–2026)

> 调研日期：2026-07-14。方法：网络检索并核实。
> 视角：以"复活一份 2016 年 LoL 数据集（22 万场 NA 排位、patch 5.21–6.1、含时间线与击杀事件）"为出发点。
> 原 2016 年工作：kill/assist 矩阵上的中心性排名（eigenvector/PageRank/HITS）、k-means/层次英雄聚类、简单 draft 与事后胜负预测。

---

## 1. Graph/network science on character interaction networks; champion/hero representation learning

- **Yang, P., Harrison, B., Roberts, D. L. — "Identifying Patterns in Combat that are Predictive of Success in MOBA Games" — FDG 2014.** Closest ancestor of kill-matrix analysis: models MOBA combat as sequences of directed player-interaction graphs (damage/heal edges, role-labeled nodes) and mines graph patterns that predict game outcome at ~80% accuracy. (fdg2014.org/papers/fdg2014_paper_36.pdf)
- **Mora-Cantallops, M., Sicilia, M.-Á. — "Player-centric networks in League of Legends" — Social Networks, vol. 52, 2018.** Builds player-interaction networks from LoL match data and relates network position to performance; the most directly comparable peer-reviewed LoL network-science work.
- **Eggert, C., Herrlich, M., Smeddinck, J., Malaka, R. — "Classification of Player Roles in the Team-Based Multi-player Game Dota 2" — ICEC 2015 (LNCS 9353).** Supervised role classification from replay-derived features; the canonical reference point for role/cluster analysis of MOBA characters.
- **Gong, L., et al. — "OptMatch" — KDD 2020 (ADS track, oral).** Learns low-dimensional hero/player representations from high-order interaction structure (evaluated on 623k LoL matches); modern successor to interaction-matrix embeddings. (github.com/fuxiAIlab/OptMatch)
- **Lee, H., et al. (dojeon-ai lab) — "DraftRec" — WWW 2022.** Hierarchical transformer over player match histories for champion recommendation + win prediction; trained on 280k LoL matches, code and data public — the modern baseline any revived draft-prediction work must compare to. (arXiv:2204.12750)
- **hero2vec-style embeddings:** no single canonical peer-reviewed paper — this exists as a family of word2vec-on-drafts implementations (swarmer/hero2vec, evanthebouncy/dota_hero_semantic_embedding on GitHub; gilgi.org blog). Useful to cite as "community practice" with OptMatch/DraftRec as the academic versions.
- **"Knowledge enhanced graph contrastive learning for match outcome prediction" — Information Processing & Management, 2024.** GNN/contrastive learning over hero knowledge graphs + player match-sequence graphs for outcome prediction（第一作者未完全核实）。
- **Sapienza, A., et al. — "Deep Neural Networks for Optimal Team Composition" — arXiv:1805.03285 (2018).** Team-composition learning from Dota 2 data; bridges clustering-era and deep-representation-era approaches.
- Indonesian-language SNA work applying degree/betweenness/closeness centrality to Dota 2 hero pick networks on ~17.8k pro matches exists (Teknomatika journal) — evidence that centrality-on-hero-graphs remains a live but under-published niche; **a rigorous English-language kill-matrix centrality paper appears to still be a gap.**

## 2. Game balance quantification, meta shifts, intransitivity

- **He, Y., Tran, C., Jiang, J., Burghardt, K., Ferrara, E., Zheleva, E., Lerman, K. — "Heterogeneous Effects of Software Patches in a Multiplayer Online Battle Arena Game" — FDG 2021 (arXiv:2110.14632).** Causal-inference framework quantifying how LoL patch changes to one champion propagate to win rates of other champions — directly relevant to cross-patch analysis of the 5.21–6.1 window.
- **Zhang, X. "A.", Keegan, B. C. — "Characterizing disruptions in online gaming behavior following software patches" — arXiv:2207.02736 (2022).** Measures behavioral disruption across 53M Dota 2 matches around patches over 30 months; patch severity correlates with magnitude of pick-behavior shifts.
- **Chitayat, A. P., Block, F., Walker, J., Drachen, A. — "Beyond the Meta: Leveraging Game Design Parameters for Patch-Agnostic Esport Analytics" — AIIDE 2023 (arXiv:2305.18477).** Uses patch notes/design parameters to build champion representations that transfer across patches — key methodological reference for making 2016-era models comparable to modern data.
- **Balduzzi, D., Tuyls, K., Perolat, J., Graepel, T. — "Re-evaluating Evaluation" — NeurIPS 2018 (arXiv:1806.02643).** Nash averaging and multidimensional Elo (mElo) decomposing win-loss matrices into transitive + cyclic components; the principled tool for measuring counter-pick (rock-paper-scissors) structure in champion matchup matrices.
- **Czarnecki, W. M., Gidel, G., Tracey, B., Tuyls, K., Omidshafiei, S., Balduzzi, D., Jaderberg, M. — "Real World Games Look Like Spinning Tops" — NeurIPS 2020 (arXiv:2004.09468).** Geometry of real games: transitive axis + non-transitive cycle width; frames how a champion-matchup dataset can test spinning-top structure empirically.
- **Lin, C.-C., Shih, Y.-W., Kuo, K.-T., Chen, Y.-C., Chen, C.-H., Chiu, W.-C., Wu, I-C. — "Identifying and Clustering Counter Relationships of Team Compositions in PvP Games for Efficient Balance Analysis" — TMLR 2024 (arXiv:2408.17180).** Bradley-Terry strength ratings + vector-quantized counter-relationship clustering as balance measures beyond win rate. Companion: **"Online Learning of Counter Categories and Ratings in PvP Games" (arXiv:2502.03998, 2025)**.
- **Zhou, H. — "Beyond Win Rates: A Clustering-Based Approach to Character Balance Analysis in Team-Based Games" — arXiv:2502.01250 (2025).** Agglomerative clustering with Jensen-Shannon divergence on agent co-occurrence for balance analysis (Valorant). ⚠️ 有共同作者撤稿请求，仅作方法学参考，谨慎引用。
- **"Metagaming and Metagames in Esports" — International Journal of Esports (2021).** Conceptual treatment of what "the meta" is and how it shifts（第一作者未完全核实）。
- **Maymin, P. Z. — "Smart kills and worthless deaths: eSports analytics for League of Legends" — Journal of Quantitative Analysis in Sports 17(1), 2021.** Win-probability-conditioned kill/death valuation on millions of LoL games; the reference for "kills are not equal" arguments and an upgrade path for the dataset's 21.7M kill events.

## 3. Datasets, benchmarks, and why a preserved 2016 dataset is rare

- **Riot API status:** match-v1/v2 fully deprecated years ago; match-v4 deprecated **Sept 13, 2021** in favor of match-v5 (riotgames.com/en/DevRel/riot-games-api-change-log). Developer-relations GitHub issues (#868, #807, #472) document that match-v5 silently drops matches older than roughly two years and returns "match not found" for older IDs. **Consequence: 2016 (patch 5.21–6.1) match and timeline data cannot be re-collected from Riot today; a preserved 220k-match SQLite archive with timelines and kill events is effectively irreplaceable primary data for longitudinal meta-evolution studies.** (Old matches also predate the PUUID migration, so identifiers in modern tooling don't even map back.)
- **Kaggle LoL datasets:** "League of Legends Ranked Matches" (paololol; ~1.8M ranked matches, 2014–2018-era, but mostly flat post-match stats), "(LoL) League of Legends Ranked Games" (datasnaek; ~50k games), plus many modern small sets (2024/2025 patches). None combine per-minute timeline deltas + raw kill events + bans + tiers for the 2015–2016 window at 220k-match scale.
- **OpenDota dump:** the last full public data dump covers >1.19B Dota 2 matches, March 2011–March 2016 (used by Lussetti & Fraser, "Big Data Reduction: Lessons Learned From Analyzing One Billion Dota 2 Matches," TRU Undergraduate Research Conf. 2019) — an important precedent showing 2016-era MOBA dumps still fuel research, but it is Dota, not LoL, and lacks LoL timeline granularity.
- **Dataset-paper exemplars in games research:**
  - **Lin, Z., Gehring, J., Khalidov, V., Synnaeve, G. — "STARDATA: A StarCraft AI Research Dataset" — AIIDE 2017 (arXiv:1708.02139).** 65k replays / 1.5B frames; the template for a game dataset paper at AIIDE.
  - **Białecki, A., et al. — "SC2EGSet: StarCraft II Esport Replay and Game-state Dataset" — Nature Scientific Data, 2023.** Shows esports match datasets are publishable in Scientific Data with tooling + PyTorch loaders.
  - **Xenopoulos, P., Silva, C. — "ESTA: An Esports Trajectory and Action Dataset" — NeurIPS 2022 Datasets & Benchmarks (arXiv:2209.09861).** 8.6M CS:GO events + awpy parser; model for pairing a dataset with benchmark tasks (win prediction).
  - **"Predicting Events in MOBA Games: Dataset, Attribution, and Evaluation" (Tencent, arXiv 2020/2021)** — MOBA event-prediction dataset paper (Honor of Kings).
  - **League of Legends Comeback Prediction Dataset — IEEE DataPort** — precedent for hosting LoL datasets on IEEE DataPort.
  - **Smerdov, A., et al. — "Collection and Validation of Psychophysiological Data from Professional and Amateur Players: a Multimodal eSports Dataset" (arXiv:2011.00958)** — further esports dataset-paper example.

## 4. 2023–2026 trends: LLMs, foundation models, agent evaluation

- **Kim, J., Lee, W., Park, J. — "Structured Summarization of League of Legends Match Data Optimized for Large Language Model Input" — Applied Sciences 15(13):7190, 2025.** LoL-MDC compresses ~80k-token Riot match JSON to <2k tokens so LLMs can generate match summaries/coaching analysis — directly applicable to the SQLite dataset as an LLM-ready corpus.
- **Zhang, Z., Cao, F., Mo, Y., Zhang, Y., Poon, J., Han, C. — "Game-MUG: Multimodal Oriented Game Situation Understanding and Commentary Generation Dataset" — arXiv:2404.19175 (2024).** LoL livestream-based dataset (text/audio/event logs) for situation understanding and audience-engaged commentary generation.
- **"AI-Generated Game Commentary: A Survey and a Datasheet Repository" — arXiv:2506.17294 (2025).** Survey mapping the game-commentary-generation space, incl. esports data-to-text（作者未逐一核实）。
- **Ma, W., et al. — "Large Language Models Play StarCraft II: Benchmarks and A Chain of Summarization Approach" (TextStarCraft II) — arXiv:2312.11865 (2023/2024).** LLM agents evaluated inside an RTS via textualized telemetry — the paradigm for "LLM reasoning over game state logs."
- **"GPT for Games: An Updated Scoping Review (2020–2024)" — arXiv:2411.00308.** Scoping review of LLM applications across game AI.
- **Agent evaluation with match data:** Balduzzi 2018 (Nash averaging) and Czarnecki 2020 (spinning tops); plus **Vinyals, O., et al. — AlphaStar — Nature 575, 2019** and **Berner, C., et al. — OpenAI Five — arXiv:1912.06680 (2019)** — both evaluate agents via large human-match ecosystems, establishing human match corpora as evaluation substrates.
- **Ye, D., et al. — "Towards Playing Full MOBA Games with Deep Reinforcement Learning" — NeurIPS 2020 (arXiv:2011.12692)** and **JueWuDraft — IEEE ToG 2021** — RL-era MOBA work whose drafting components connect back to draft-based win prediction.

## 5. Publication venues and fit

| Venue | Fit |
|---|---|
| **IEEE Transactions on Games (ToG)** | LoL/MOBA win-prediction and balance work（Hodge et al. 2021；Hitar-García et al. 2023） |
| **AIIDE (AAAI)** | Dataset papers (STARDATA 2017) + esports analytics (Beyond the Meta 2023) — 数据集+基准论文的强匹配 |
| **FDG** | Patch-effect and combat-graph work（He et al. 2021；Yang et al. 2014）；有成熟 data/analytics track |
| **IEEE CoG (原 CIG)** | MOBA analytics 常规阵地 |
| **ACM CHI PLAY** | 玩家行为视角（段位/行为框架） |
| **KDD ADS / WWW** | 规模化方法型工作（OptMatch KDD 2020；DraftRec WWW 2022） |
| **Nature Scientific Data / NeurIPS D&B / IEEE DataPort / Zenodo+HuggingFace** | 电竞数据集论文的成熟归宿（SC2EGSet；ESTA；LoL Comeback dataset） |

综述引用：**Mora-Cantallops & Sicilia, "MOBA games: A literature review," Entertainment Computing 26, 2018**（DOI 10.1016/j.entcom.2018.02.005）。

## Cross-cutting takeaways

1. 数据集的独特卖点已核实：Riot API 保留期（match-v5 约两年，v4 自 2021 死亡）使 patch 5.21–6.1 的 timeline + 击杀事件数据今日不可恢复；可比公共档案（Kaggle、OpenDota-for-Dota）缺乏该窗口的 LoL timeline/击杀粒度。
2. 2016 年的每项分析都有直接的现代升级路径与强 baseline：centrality → mElo/Nash averaging + spinning-top 几何；聚类 → 共现/JSD 与补丁说明书驱动的表示；draft 预测 → DraftRec/OptMatch 级 transformer 与 GNN。
3. 严格的英文"英雄击杀矩阵中心性"论文仍是空白——最接近的是 Yang et al. 2014（战斗图）、Mora-Cantallops & Sicilia 2018（玩家网络）与非英文的 Dota 英雄网络 SNA 工作。
4. 2023–2026 的 LLM 浪潮（LoL-MDC、Game-MUG、TextStarCraft II）为数据集提供了第二生命：LLM 输入语料（比赛总结、教练、解说），超越经典分析。

**核实注记**：以上论文除标注"未完全核实"者外，第一作者/venue 均经检索确认；arXiv:2502.01250 有撤稿请求待决；"Commentary Generation from Data Records of Multiplayer Strategy Esports Game"（arXiv:2212.10935，LoL data-to-commentary）存在但作者名单未确认，视为线索。

## Sources

[Riot API change log](https://www.riotgames.com/en/DevRel/riot-games-api-change-log) · [developer-relations #868](https://github.com/RiotGames/developer-relations/issues/868) · [FDG 2014 Yang et al.](http://www.fdg2014.org/papers/fdg2014_paper_36.pdf) · [Social Networks 2018](https://www.sciencedirect.com/science/article/abs/pii/S0378873318301229) · [Re-evaluating Evaluation](https://arxiv.org/abs/1806.02643) · [Spinning Tops](https://arxiv.org/abs/2004.09468) · [He et al. FDG 2021](https://arxiv.org/abs/2110.14632) · [Zhang & Keegan](https://arxiv.org/abs/2207.02736) · [Beyond the Meta](https://arxiv.org/abs/2305.18477) · [Lin et al. TMLR](https://arxiv.org/abs/2408.17180) · [Counter categories](https://arxiv.org/abs/2502.03998) · [Beyond Win Rates](https://arxiv.org/abs/2502.01250) · [Maymin JQAS](https://www.degruyterbrill.com/document/doi/10.1515/jqas-2019-0096/html) · [DraftRec](https://arxiv.org/abs/2204.12750) · [OptMatch](https://www.kdd.org/kdd2020/accepted-papers/view/optmatch-optimized-matchmaking-via-modeling-the-high-order-interactions-on-.html) · [STARDATA](https://arxiv.org/abs/1708.02139) · [SC2EGSet](https://www.nature.com/articles/s41597-023-02510-7) · [ESTA](https://arxiv.org/abs/2209.09861) · [LoL-MDC](https://doi.org/10.3390/app15137190) · [Game-MUG](https://arxiv.org/abs/2404.19175) · [TextStarCraft II](https://arxiv.org/abs/2312.11865) · [Hodge et al. IEEE ToG](https://eprints.whiterose.ac.uk/152931/) · [Kaggle paololol](https://www.kaggle.com/datasets/paololol/league-of-legends-ranked-matches) · [Kaggle datasnaek](https://www.kaggle.com/datasets/datasnaek/league-of-legends) · [Lussetti & Fraser](https://www.researchgate.net/publication/332110190_Big_Data_Reduction_Lessons_Learned_From_Analyzing_One_Billion_Dota_2_Matches) · [MOBA literature review](https://www.sciencedirect.com/science/article/abs/pii/S1875952117300149) · [Eggert et al. ICEC 2015](https://link.springer.com/chapter/10.1007/978-3-319-24589-8_9) · [IEEE DataPort LoL dataset](https://ieee-dataport.org/documents/league-legends-comeback-prediction-dataset) · [OpenAI Five](https://arxiv.org/abs/1912.06680) · [IPM 2024 graph contrastive](https://www.sciencedirect.com/science/article/abs/pii/S0306457324003698)
