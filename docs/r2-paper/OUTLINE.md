# R2 论文骨架（草案 v0.1，2026-07-15）

## 标题候选

1. *How Much Rock-Paper-Scissors Is There in League of Legends? A Noise-Corrected
   Decomposition of Champion Matchup Structure*
2. *Transitive Strength Dominates Counter-Picks: Quantifying Cyclic Structure in
   220K Ranked MOBA Matches*
3. *Counter-Pick Structure in MOBA Matchups Is Small, Stable — and Easily
   Overestimated*

（推荐 1 或 3：把方法学警示放进标题，是本文最锋利的卖点。）

## 目标 venue（按优先级）

1. **IEEE Transactions on Games**（期刊，滚动投稿；Hodge/mElo 类方法 + 大规模实证的合适归宿）
2. **IEEE CoG 2027**（会议备选，通常 1–2 月截稿）
3. **FDG 2027**（重实证的 data track）

**发表策略（2026-07-15 定）：与 R1 数据集论文分投**，本文引用 R1 为数据来源
（R1 先挂 Zenodo DOI 即可引用，无需等其见刊）。
与 2016 年旧分析的逐条对应关系（Related Work / Discussion 素材）见
[docs/LEGACY_CONNECTIONS.md](../LEGACY_CONNECTIONS.md) 第三节。

## Abstract 草稿（含真实数字）

> Counter-pick ("rock-paper-scissors") relationships between champions are
> central to MOBA folklore and to a growing literature on drafting AI, yet how
> much of the game's matchup structure they actually explain has never been
> measured. Using an irreplaceable archive of 222,652 ranked League of Legends
> matches from Pre-Season 2016 (5.57M champion-pair observations), we decompose
> pairwise win log-odds into a transitive strength rating and a cyclic residual
> via weighted HodgeRank. We first show that the naive cyclic share is a
> sample-size artifact: on outcome-permuted data with identical pairing
> structure, ~92% of energy appears "cyclic". After subtracting the permutation
> null, genuine counter-pick structure accounts for only ~5% of matchup signal
> (5.1%, bootstrap 95% CI [3.6%, 7.7%]), a figure that is remarkably stable across skill tiers
> (3.6–6.0%) and game patches (3.6–4.4%). Transitive ratings reproduce
> raw win-rate rankings and their movements track balance-patch changes,
> while the strongest cyclic pairs recover community-known counter matchups.
> Our results imply that draft-phase win prediction is dominated by additive
> champion strength — consistent with the ~55% accuracy ceiling we replicate
> (logistic regression 54.7% cross-patch / 55.5% same-patch) — and provide a
> corrected estimator for future balance-analysis work.

## 论文结构

1. **Introduction**
   - MOBA 平衡性与克制关系的民间叙事 vs 缺乏量化
   - 三个贡献：(i) 噪声校正的循环分量估计器（置换零假设能量扣除）；
     (ii) 首次对 LoL 英雄克制占比的大规模测量（~5%，跨段位/补丁稳定）；
     (iii) 不可再生的 2016 数据档案 + 可复现管线
2. **Related Work**（素材见 docs/literature/）
   - 博弈结构评估：Balduzzi 2018 (Nash averaging/mElo)、Czarnecki 2020 (spinning tops)、
     Lin 2024 (TMLR counter clustering)
   - MOBA 平衡/补丁研究：He 2021 (FDG)、Zhang & Keegan 2022、Chitayat 2023 (AIIDE)
   - Draft 预测与推荐：Semenov 2016、DraftRec 2022、Kim 2020 (calibration)
   - 与 HodgeRank（Jiang et al. 2011, Math. Program.）的联系 — 引用补充 TODO
3. **Data**（引用 R1 数据集论文/数据卡）
   - 222,652 场 NA 排位、patch 5.21–6.1、tier 分布、清洗规则（<10min 剔除、击杀去重）
4. **Method**
   - 对位矩阵构造（每场 25 对、双向折叠消蓝方优势）
   - 加权 HodgeRank 分解；log-odds + Laplace 平滑
   - **置换零假设校正**（match 级置换保留场内相关）；bootstrap CI
5. **Results**
   - 5.1 原始 vs 校正循环占比（核心表：7 切片 × raw/corrected/S-N）
     - 关键数字：raw 27–58% vs corrected 3.6–6.0%；置换零假设下 raw ≈ 92%
   - 5.2 跨段位稳定性（低/中/高：3.6/6.0/4.8%）
   - 5.3 跨补丁稳定性与 meta 演化（analysis/output/matchup_extended.md）：
     相邻 build 评分 Spearman 0.60–0.77（meta 真实移动 + 小样本噪声并存）；
     top movers 与补丁史吻合（如波比重做恰在 5.24.0.256 边界增益 +0.22）；
     **build 级 cyclic residual 相邻相关 ≈ 0** —— 单 build 样本量下克制估计
     被噪声主导，进一步支撑本文方法学警示
   - 5.4 外部效度：评分 Top10 与胜率榜逐名一致；最强克制对通过玩家常识检验
     （奥拉夫>德莱厄斯、凯南>鳄鱼、劫>维克兹）；击杀代理独立分析给出同量级
     循环占比（7.6%）
   - 5.5 对 draft 预测的推论：T1 基准（LR 54.7% 跨补丁 / 55.5% 同补丁，
     GBT 略低，ECE 报告）→ 加性强度主导 → 与 ~55% 文献天花板一致
6. **Discussion**
   - 对文献中朴素 mElo/循环占比结论的方法学警示
   - 局限：单区/单窗口/solo queue（非职业）、无分路对位、tier 为上赛季段位
   - 对游戏平衡设计的含义（克制层薄 → 平衡以强度调为主）
7. **Reproducibility**：代码 + 匿名化数据（Zenodo DOI TODO）

## 图表清单

- Fig 1: 分解示意（A = gradient + cyclic）
- Fig 2: raw vs corrected cyclic share 柱状（7 切片 + 置换基线 92% 参考线）— 核心图
- Fig 3: build 级 rating 演化热图/折线（top movers 标注）
- Fig 4: 可靠性图（draft 基准校准曲线）
- Table 1: 数据集概览；Table 2: 切片分解结果；Table 3: 最强克制对；
  Table 4: T1 基准结果

## 待办（写作前必须补齐）

- [x] matchup_extended 结果回填（bootstrap CI、build 演化数字）
- [ ] HodgeRank 原始文献引用核实（Jiang, Lim, Yao, Ye 2011）
- [ ] 校正估计器的偏差讨论（信号-噪声正交性假设；小切片 max(0,·) 截断偏差）
- [ ] 与 Lin et al. TMLR 2024 的方法对比段落
- [ ] 图 2/3 绘制（用 dataviz 规范）
