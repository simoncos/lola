# Literature Review: Player Modeling & Anomaly Detection in Online Games / Esports (2016–2026)

> 调研日期：2026-07-14。方法：网络检索并核实（venue 页面、arXiv、ACM DL、IEEE Xplore、ACL Anthology）。
> 覆盖：技能评级/匹配、作弊/小号/机器人检测、流失预测、LoL 毒性/挂机行为、行为聚类/角色识别。
> 每条注明数据来源，特别标注是否使用与本项目类似的 Riot API 排位赛数据。

---

## 1. Skill Rating & Matchmaking

| # | Paper | Venue / Year | Contribution | Data |
|---|-------|--------------|--------------|------|
| 1 | **T. Minka**, R. Cleven, Y. Zaykov — *TrueSkill 2: An Improved Bayesian Skill Rating System* | Microsoft Research TR, 2018 | Extends TrueSkill with per-player performance stats (kills, quits, squad membership, cross-mode skill); match-outcome prediction accuracy 52% → 68% | Halo 5 / Gears of War telemetry (proprietary; conceptually close to per-player ranked match stats). Not Riot data |
| 2 | **A. Ebtekar**, P. Frans — *Elo-MMR: A Rating System for Massive Multiplayer Competitions* | The Web Conference (WWW), 2021 | Bayesian rating for many-participant ranked competitions; incentive-compatible, outperforms Elo/Glicko/TrueSkill on prediction | Codeforces/Topcoder contest histories (public); applicable to games but not evaluated on MOBA data |
| 3 | **L. Gong** et al. — *OptMatch: Optimized Matchmaking via Modeling the High-Order Interactions on the Arena* | KDD, 2020 | Two-stage neural matchmaking: learns player embeddings capturing inter-personal/team-up effects offline, optimizes player utility online | NetEase commercial game logs (MOBA-like); proprietary |
| 4 | **M. Aung**, V. Bonometti, P. Cowling, A. Kokkinakis, C. Yoder, A. Wade et al. — *Predicting Skill Learning in a Large, Longitudinal MOBA Dataset* | IEEE CIG, 2018 | Predicts long-run player skill/rank trajectory from early-match behavioral features; ~400k LoL players from the 2016 season | **LoL 2016-season ranked match data (Riot-derived)** — closest published analog to a 220k-match 2016 Riot API dataset |
| 5 | **Z. Chen** et al. — *Player Skill Decomposition in Multiplayer Online Battle Arenas* | arXiv:1702.06253, 2017 | Decomposes MOBA skill into interpretable sub-skills (e.g., farming, fighting) via matrix factorization over per-match stats | Public MOBA match data (Dota-2-style telemetry) |

Also relevant: *PandaSkill* (arXiv:2501.10049, 2025) — ML-estimated per-player performance ratings from individual stats over 5 years of **professional LoL** matches; and *CUPID* (arXiv:2406.19720) re-matchmaking for MOBA fairness/position satisfaction.

**Open**: neural rating systems for amateur ranked MOBA play using public API data remain rare — most strong work uses proprietary publisher telemetry; rank/tier prediction from behavioral features at scale (Aung 2018) has few follow-ups.

---

## 2. Cheating / Smurf / Bot / Boosting / Match-Fixing Detection

| # | Paper | Venue / Year | Contribution | Data |
|---|-------|--------------|--------------|------|
| 1 | **E. Lee**, J. Woo, H. Kim, A. Mohaisen, H.K. Kim — *You Are a Game Bot! Uncovering Game Bots in MMORPGs via Self-similarity in the Wild* | NDSS, 2016 | Self-similarity of action sequences as a general bot signature; F ~0.96 with RF/SVM/MLP | Production logs from Lineage, Aion, Blade & Soul (NCSOFT, proprietary) |
| 2 | **A.R. Kang** et al. — *Multimodal Game Bot Detection Using User Behavioral Characteristics* | SpringerPlus, 2016 | Combines multiple behavior modalities (actions, social, economic) for MMORPG bot detection | Commercial MMORPG logs (proprietary) |
| 3 | **A. Jonnalagadda** et al. (UCSB + NVIDIA) — *Robust Vision-Based Cheat Detection in Competitive Gaming* | Proc. ACM CGIT (PACMCGIT), 2021 | DNN on final frame buffer detects wallhack overlays; near-zero false positives, adversarially robust (IBP + uncertainty) | Custom dataset from 2 FPS games × 3 cheat tools |
| 4 | **J.C. Monge**, N.L. Matthews — *Blaming the Smurf: Using a Novel Social Deception Behavior in Online Games to Test Attribution Theories* | New Media & Society, 2025 | First empirical treatment of smurfing as deception/toxicity: 69% of players admit smurfing; attribution experiments | Player surveys/experiments — **no telemetry-based detector** |
| 5 | **(Anon.) team** — *AI-based Betting Anomaly Detection System to Ensure Fairness in Sports and Prevent Illegal Gambling* | Scientific Reports, 2024 | RF/KNN/ensemble on betting-odds streams detect fixed matches (>92% acc.) — nearest methodological template for esports match-fixing | Football betting-odds data from 12 bookmakers; **not esports** |

Related context: *Match-Fixing in Esports: A Scoping Review of Skin-Betting* (Zohn & Bleakley, 2024) and *The Dark Side of E-sports* (Int. J. Esports) review cheating/doping/fixing but present **no detection models**; recent arXiv work exists on server-side aimbot detection via deep learning (arXiv:2607.04336, 2026) and human-AI collaborative MMORPG bot detection (arXiv:2508.20578).

**Open / data-starved (strongest gap found)**: essentially **no peer-reviewed telemetry-based detector for smurfing, elo-boosting, or account-sharing in MOBAs** — the state of the art lives in industry patents (Riot/Blizzard fraud-detection patents, US10992972, US11495086) and Riot dev blogs, not papers. Esports match-fixing detection has *zero* dedicated empirical papers (only scoping reviews + sports-betting analogs). A labeled public dataset for smurf/boost detection from ranked match histories would be genuinely novel — a 220k-match Riot API dataset with per-account match sequences is exactly the kind of data this gap needs (label acquisition is the hard part).

---

## 3. Churn Prediction & Retention

| # | Paper | Venue / Year | Contribution | Data |
|---|-------|--------------|--------------|------|
| 1 | **Á. Periáñez**, A. Saas, A. Guitart, C. Magne — *Churn Prediction in Mobile Social Games: Towards a Complete Assessment Using Survival Ensembles* | IEEE DSAA, 2016 | Survival ensembles predict *time-to-churn* per player under censoring; beats Cox regression | Mobile F2P social-game logs (proprietary) |
| 2 | **M. Tamassia**, W. Raffe, R. Sifa, A. Drachen, F. Zambetta, M. Hitchens — *Predicting Player Churn in Destiny: A Hidden Markov Models Approach…* | IEEE CIG, 2016 | HMMs over behavioral state sequences to predict departure in a hybrid AAA online title | Destiny telemetry (Bungie, proprietary) |
| 3 | **S. Demediuk**, A. Murrin, D. Bulger, M. Hitchens, A. Drachen et al. — *Player Retention in League of Legends: A Study Using Survival Analysis* | Australasian Computer Science Week (ACSW), 2018 | Mixed-effects Cox regression on LoL match histories; inter-match gap duration is the dominant churn signal | **LoL ranked match histories (Riot API-style data)** — directly comparable to a 2016 Riot API dataset |
| 4 | **E. Lee, Y. Jang, D. Yoon, J. Jeon** et al. — *Game Data Mining Competition on Churn Prediction and Survival Analysis Using Commercial Game Log Data* | IEEE Trans. on Games, 2018 (arXiv:1802.02301) | Benchmark competition (IEEE CIG 2017): 100GB Blade & Soul logs, 10k players; deep learning + tree boosting won both churn and survival tracks | NCSOFT Blade & Soul logs (released for competition) |
| 5 | **J. Kristensen** et al. — *Combining Sequential and Aggregated Data for Churn Prediction in Casual Freemium Games* | IEEE CoG 2019 (arXiv:2209.03184) | Hybrid LSTM-on-sequences + aggregate-feature model outperforms either alone | Casual freemium game logs (proprietary) |

**Open**: churn work is dominated by mobile/MMO proprietary data; only Demediuk 2018 targets LoL specifically. Session-sequence churn modeling on *public* Riot API data (definable churn = no ranked match in N days) is feasible and underexplored; social/party-network churn contagion in MOBAs (cf. Applied Network Science 2022 for mobile F2P) is untested on LoL.

---

## 4. Toxicity / AFK / Griefing Detection in LoL

| # | Paper | Venue / Year | Contribution | Data |
|---|-------|--------------|--------------|------|
| 1 | **J. Blackburn**, H. Kwak — *STFU NOOB! Predicting Crowdsourced Decisions on Toxic Behavior in Online Games* | WWW, 2014 (foundational, pre-window) | RF on 534 features (chat, performance, reports) predicts Tribunal verdicts | **LoL Tribunal dataset** (~1M cases, crowdsourced labels; now defunct — Riot closed Tribunal) |
| 2 | **M. Märtens**, S. Shen, A. Iosup, F. Kuipers — *Toxicity Detection in Multiplayer Online Games* | NetGames, 2015 | Chat-log toxicity detector tied to match phases/outcomes in MOBA | Dota 2 chat logs from public replays |
| 3 | **Y. Kou** — *Toxic Behaviors in Team-Based Competitive Gaming: The Case of League of Legends* | CHI PLAY, 2020 | Player-grounded taxonomy: 5 toxic behavior types (incl. **intentional feeding and AFK/griefing**) + 5 contextual triggers | Qualitative LoL player data (no telemetry) |
| 4 | **H. Weld** et al. — *CONDA: a CONtextual Dual-Annotated Dataset for In-game Toxicity Understanding and Detection* | Findings of ACL, 2021 | 45K utterances / 1.9K matches, joint intent + slot-level toxicity annotation; the standard public in-game toxicity benchmark | Dota 2 chat logs (public dataset) |
| 5 | **J.C. Aguerri**, M. Santisteban, F. Miró-Llinares — *The Enemy Hates Best? Toxicity in League of Legends and Its Content Moderation Implications* | Eur. J. on Criminal Policy and Research, 2023 | Measured prevalence in 328 competitive LoL matches: 70% of games affected, 30% of players toxic; LoL-tailored taxonomy | Hand-coded LoL match chat/behavior |

Also: **GameTox** (Naseem, Shiwakoti, Shah, Thapa, Zhang — NAACL 2025 Short): 53K game-chat utterances with intent+slot toxicity labels; *"bot lane noob": Towards Deployment of NLP-based Toxicity Detectors in Video Games* (arXiv:2604.10175, 2026) builds L2DTnH — 1.4k toxic / 13.8k non-toxic LoL messages re-annotated from Tribunal data — and shows general-purpose detectors underperform in LoL chat.

**Open / data-starved**: chat toxicity is well covered; **behavioral griefing (AFK, intentional feeding, trolling picks) detection from match telemetry has almost no academic literature** — it exists only in Riot's behavioral-systems dev blogs (2020–2025 automated inting/AFK detection). Kou 2020 defines the taxonomy but no one has published a telemetry-based classifier. Ranked match data with per-player timelines (deaths, item sales, position idleness) would support a first academic AFK/feeding detector; labels are the bottleneck (heuristic/weak labels needed since report data is private).

---

## 5. Behavior Clustering / Playstyle Profiling / Role Identification

| # | Paper | Venue / Year | Contribution | Data |
|---|-------|--------------|--------------|------|
| 1 | **H.Y. Ong**, S. Deolalikar, M. Peng — *Player Behavior and Optimal Team Composition for Online Multiplayer Games* | arXiv:1503.02230, 2015 | Unsupervised behavior clusters of LoL players → team-composition features predict outcomes | **LoL match data (Riot API)** |
| 2 | **C. Eggert**, M. Herrlich, J. Smeddinck, R. Malaka — *Classification of Player Roles in the Team-Based Multi-player Game Dota 2* | ICEC (Entertainment Computing), 2015 | Supervised role classification (carry/support etc.) from low-level parsed replay features | Dota 2 replay data |
| 3 | **S. Demediuk**, P. York, A. Drachen, J.A. Walker, F. Block — *Role Identification for Accurate Analysis in Dota 2* | AAAI AIIDE, 2019 | Ensemble clustering assigns per-hero roles from map movement (first 10 min), resource priority, ability order — the canonical role/lane-inference method | Dota 2 match telemetry (OpenDota-style) |
| 4 | **F. do Nascimento Junior** et al. — *Profiling Successful Team Behaviors in League of Legends* | ACM WebMedia, 2017 | Clusters team behavior profiles and links them to win rates in LoL | **LoL ranked match data via Riot API** |
| 5 | **(UMD/collab.)** — *"Can You Play Anything Else?" Understanding Play Style Flexibility in League of Legends* | arXiv:2402.05865, 2024 | Quantifies champion/role flexibility vs. specialization from longitudinal LoL match histories and links it to performance | **Large-scale LoL match histories (Riot API)** |

Also: *A Supervised Clustering Approach for Subrole Discovery in a MOBA Game* (Springer LNCS, 2024) — finer-grained subroles beyond the 5 standard positions; Ahmad et al. 2019 spatio-temporal team-coordination clustering in Dota 2.

**Open**: role/lane inference is solved for Dota 2 (Demediuk 2019) but has no equally canonical published equivalent for LoL — pre-2017 Riot API match records lack reliable role/lane labels (the API's `lane`/`role` fields are known to be noisy), so replicating Demediuk-style positional-inference on 2016 LoL timeline data is a legitimate, publishable gap. Cross-patch/cross-season stability of playstyle clusters is also underexplored.

---

## Summary of Gaps (ranked by openness)

1. **Smurf / boosting / account-sharing detection in MOBAs** — no peer-reviewed telemetry-based detectors; only perception studies (Monge 2025), patents, and vendor blogs. Highest novelty; label acquisition is the core obstacle.
2. **Esports match-fixing detection** — zero empirical papers; only scoping reviews (Zohn & Bleakley 2024) and a sports-betting-odds analog (Sci. Reports 2024). Requires odds or pro-match data, not ranked-ladder data.
3. **Behavioral griefing/AFK/inting detection from LoL telemetry** — taxonomy exists (Kou 2020), industry systems exist (Riot dev blogs), academic detectors do not. Feasible with per-match timeline data + weak labels.
4. **Role/lane inference for LoL** (esp. historical 2016-era data with noisy API labels) — solved for Dota 2, not canonically for LoL.
5. **Neural skill-rating / rank prediction on public Riot data** — some work (Aung 2018 used 2016-season LoL data very similar to a 220k-match Riot API corpus), but modern sequence models on public ranked data remain sparse.
6. **Churn** is the most saturated subarea, though LoL-specific churn beyond Demediuk 2018 is thin.

## Sources (key URLs)

[TrueSkill 2](https://www.microsoft.com/en-us/research/publication/trueskill-2-improved-bayesian-skill-rating-system/) · [Elo-MMR (WWW'21)](https://dl.acm.org/doi/abs/10.1145/3442381.3450091) · [OptMatch (KDD'20)](https://dl.acm.org/doi/abs/10.1145/3394486.3403279) · [Aung et al. CIG'18](https://ieeexplore.ieee.org/document/8490431/) · [Chen skill decomposition](https://arxiv.org/pdf/1702.06253) · [PandaSkill](https://arxiv.org/abs/2501.10049) · [You Are a Game Bot (NDSS'16)](https://davidmohaisen.github.io/files/ndss16.pdf) · [Vision-based cheat detection](https://arxiv.org/abs/2103.10031) · [Blaming the smurf](https://journals.sagepub.com/doi/abs/10.1177/14614448241235638) · [Betting anomaly detection (Sci. Reports 2024)](https://www.nature.com/articles/s41598-024-57195-8) · [Match-fixing scoping review](https://cdspress.ca/wp-content/uploads/2024/01/Zohn-Bleakley.pdf) · [Periáñez survival ensembles](https://arxiv.org/abs/1710.02264) · [Tamassia Destiny churn](https://dl.acm.org/doi/10.1109/CIG.2016.7860431) · [LoL retention survival analysis](https://dl.acm.org/doi/10.1145/3167918.3167937) · [Game Data Mining Competition](https://arxiv.org/abs/1802.02301) · [CONDA](https://arxiv.org/abs/2106.06213) · [Kou CHI PLAY'20](https://dl.acm.org/doi/10.1145/3410404.3414243) · [Aguerri 2023](https://link.springer.com/article/10.1007/s10610-023-09541-1) · [GameTox (NAACL'25)](https://aclanthology.org/2025.naacl-short.37/) · ["bot lane noob"](https://arxiv.org/abs/2604.10175) · [Ong et al.](https://arxiv.org/abs/1503.02230) · [Demediuk role identification (AIIDE'19)](https://ojs.aaai.org/index.php/AIIDE/article/view/5235) · [Profiling Successful Team Behaviors (WebMedia'17)](https://dl.acm.org/doi/abs/10.1145/3126858.3126886) · [Play Style Flexibility in LoL](https://arxiv.org/pdf/2402.05865) · [Märtens toxicity](https://atlarge-research.com/pdfs/2015-martens-toxicity.pdf)
