# LoLA 研究路线图（2026）

> 基于对本仓库代码、数据集与 2016–2026 年 MOBA/电竞数据分析文献的调研，
> 梳理"接下来还能做什么研究"。文献均经过检索核实（引用见文末）。

---

## 1. 项目现状盘点

### 1.1 数据集（核心资产）

| 表 | 记录数 | 内容 |
|---|---|---|
| Match | 222,652 | NA 区 Ranked-SOLO-5x5，Pre-Season 2016（patch 5.21–6.1） |
| Summoner | 487,484 | 玩家 ID + 是否已爬取 |
| Participant | 2,226,520 | 每人每场 40+ 项终局统计（KDA、经济、三类伤害、视野等） |
| ParticipantTimeline | 8,906,080 | 分段时间线（补刀/经济/经验/承伤 per-min delta 及对线差值） |
| FrameKillEvent | 21,692,852 | 击杀事件（时间、击杀者、被杀者、助攻） |
| Team / TeamBan | 445,304 / 1,330,757 | 队伍结果、大小龙、禁用 |

另含派生表：英雄击杀/助攻矩阵、counter/partner 共现矩阵、分 tier/version 标注。
SQLite 约 2.1GB，已通过 Google Drive 共享。

### 1.2 已完成的分析（2016 年代方法）

- **英雄能力排名**：kill/assist 矩阵上的特征向量中心性、HITS、PageRank，多种归一化（按 picks、按对位共现）。
- **英雄聚类**：11 维终局统计上的 k-means 与层次聚类（k=6，肘部法选择）。
- **英雄推荐**：胜率/热度榜 + bibliographic coupling（相似英雄、最佳搭档、counter 推荐）。
- **胜负预测**：阵容特征赛前预测 ~50%（等于随机）；终局统计事后预测 ~90%。

### 1.3 代码现状

Python 2/3 混杂、`pandas.ix` 等已废弃 API、按数据库行序去重击杀事件（代码内 TODO 已自认隐患）、无测试。任何后续研究都建议先做一轮工程现代化（见 §5）。

---

## 2. 关键判断：这份数据今天的独特价值

1. **不可再采集**。Riot match-v4 API 已于 2021-09 废弃，match-v5 只保留约两年内的比赛（developer-relations #868 等 issue 证实），且 2016 年账号 ID 早于 PUUID 迁移。**patch 5.21–6.1 的带 timeline + 击杀事件的比赛数据今天无法从官方渠道重新获得。**
2. **公开替代品缺位**。Kaggle 上的 LoL 数据集（paololol ~180 万场、datasnaek ~5 万场等）均缺少该窗口下"分钟级时间线 + 原始击杀事件 + 禁用 + 段位"的组合；OpenDota 2011–2016 大转储是 Dota 2 而非 LoL。
3. **文献里有先例**。STARDATA（AIIDE 2017）、SC2EGSet（Nature Scientific Data 2023）、ESTA（NeurIPS D&B 2022）证明"精心整理的游戏比赛数据集 + 基准任务"本身就是可发表的成果。

结论：**数据集本身就是第一篇论文**，其余研究都可以挂靠在它上面。

---

## 3. 文献综述要点（2016–2026）

### 3.1 赛前（BP 阵容）胜负预测：~55% 是公认天花板
- DraftRec（WWW 2022）在 28 万场高分段 LoL 数据上，Transformer 也只有 54.6–55.2%；Semenov（AIST 2016）发现分段越高信号越弱（AUC 0.71→0.66）。
- 原因已被领域公认：匹配系统主动配平、执行/沟通不可见、**补丁非平稳性**。Kim et al.（IEEE CoG 2020）把它形式化为不可约的标签噪声，并转向校准（calibration）研究。
- **本项目当年阵容预测 ~50% 并不是失败，只是缺少交互结构建模（FM/Transformer 可到 ~55%），且"50→55"的差距本身就是研究对象。**
- 报 70–89% 准确率的论文普遍存在数据偏斜或泄漏（玩家/队伍身份、低分段公开局）。

### 3.2 实时（局内）胜率预测已成主流
胜率曲线共识形状：开局 ~55% → 10 分钟 ~70–75% → 后期 85%+。代表作：Hodge et al.（IEEE ToG 2021，职业比赛实时部署，5 分钟后 85%）、Winning Tracker（WWW 2022，NetEase）、TSSTN（可解释、用于直播解说）、MOBA-Slice（IJCAI-W 2018）。研究重心已从"准确率"转向可解释性、校准、细粒度事件预测（如 Time to Die，CoG 2019：预测 5 秒内谁会死）。

### 3.3 BP 推荐的方法演进
关联规则（Hanke & Chaimowicz，AIIDE 2017）→ MCTS + 胜率价值函数（DraftArtist，RecSys 2018）→ 自博弈策略网络 + 树搜索（JueWuDraft，IEEE ToG 2021）→ 个性化 Transformer（DraftRec，WWW 2022）。公认缺口：**循环评估**（推荐系统用自己学的胜率模型来评估自己）、ban 建模薄弱、无跨补丁鲁棒性方案。

### 3.4 英雄关系图与平衡性度量（与本项目最贴近）
- **严格的英文"kill-matrix 中心性"论文至今仍是空白**——最接近的是 Yang et al.（FDG 2014，战斗交互图模式挖掘）与 Mora-Cantallops & Sicilia（Social Networks 2018，玩家网络而非英雄网络）。本项目 2016 年的做法在学术上仍未被人正式做掉。
- 现代升级工具已就绪：**Nash averaging / mElo**（Balduzzi et al., NeurIPS 2018）可把对局胜负矩阵分解为"传递性强度 + 循环克制"两部分；**spinning-top 几何**（Czarnecki et al., NeurIPS 2020）给出真实游戏克制结构的理论框架；Lin et al.（TMLR 2024）用 Bradley-Terry + 向量量化做克制关系聚类以量化平衡性。
- 补丁效应研究成型：He et al.（FDG 2021，LoL 补丁的因果传播效应）、Zhang & Keegan（2022，5300 万场 Dota 跨 30 个月的补丁扰动）、Beyond the Meta（AIIDE 2023，用补丁说明书构建跨补丁可迁移的英雄表示）。

### 3.5 玩家建模与异常检测：最大的学术空白区
- **MOBA 小号（smurf）/代练（boosting）/账号共享检测：没有任何同行评审的基于遥测数据的检测器**——只有认知研究（Monge 2025：69% 玩家承认开过小号）、Riot/Blizzard 专利和厂商博客。
- **挂机/故意送人头（AFK/inting）行为检测**：Kou（CHI PLAY 2020）给了分类学，Riot 有内部系统，但学术界没有公开的遥测检测模型。聊天毒性检测反而已经很卷（CONDA ACL 2021、GameTox NAACL 2025）。
- 技能评级/段位预测：Aung et al.（IEEE CIG 2018）用的正是 2016 赛季 40 万玩家 LoL 数据（与本数据集同源同期），后续跟进很少。流失预测唯一 LoL 专门研究是 Demediuk et al.（ACSW 2018，生存分析）。
- LoL 的分路/角色推断没有像 Dota 2（Demediuk et al., AIIDE 2019）那样的权威方法，而 2016 年 Riot API 的 lane/role 字段公认噪声大。

### 3.6 2023–2026 前沿：LLM 与游戏数据
LoL-MDC（Applied Sciences 2025）把 8 万 token 的 Riot 比赛 JSON 压缩成 <2k token 供 LLM 做比赛总结/教练分析；Game-MUG（2024）做 LoL 直播解说生成；TextStarCraft II（2023）确立"LLM 读文本化遥测打游戏/分析游戏"的范式。历史比赛语料作为 LLM 评测/微调数据是一条新赛道。

---

## 4. 推荐研究清单（按性价比排序）

### ⭐ T1：吃独家数据红利，工作量可控

**R1. 数据集论文：《LoLA-2016: A Preserved League of Legends Match Archive with Timelines and Kill Events》** — *✅ 初稿完成，见 `docs/r1-dataset-paper/PAPER_DRAFT.md`*
- 做法：清洗去重 → 匿名化玩家 ID → 转 Parquet/HuggingFace → 写数据卡 + 3 个基准任务（draft 胜率预测 / 实时胜率 / 英雄克制矩阵）+ 加载工具。
- 卖点：官方 API 已无法回采 2016 数据的时间线+击杀事件粒度，该组合档案不可再生；模板参照 STARDATA、SC2EGSet、ESTA。
- 目标：NeurIPS Datasets & Benchmarks / Nature Scientific Data / AIIDE / IEEE DataPort。
- 状态：工具链/审计/匿名化导出/T1+T3 基准/正文初稿全部完成；余 ToS 复核与 Zenodo/HF 发布。

**R2. 英雄克制结构的博弈论分解（直接升级原 centrality 工作）** — *分析已完成；⚠️ 新颖性降级*
- 做法：在 kill/对位胜负矩阵上做 HodgeRank 传递/循环分解 + 置换噪声校正，按 tier × patch 切片。
- ⚠️ **2026-07-15 新颖性对抗审查结论**（见 `docs/literature/04-novelty-check-2026.md`）：
  "首次分解"定位被抢先——方法归 Hamilton et al. 2024 与 Strang 2022；定性结论归
  Chen & Joachims 2016；MOBA 反制建模归 Lin & Wu 2024/2025。**幸存创新点仅为"组合 +
  真实历史 LoL 数据 + 段位/补丁稳定性 + 置换校正工具 + 第二证据链"。**
- **✅ 决策已定（用户确认）**：并入 R1 作旗舰演示分析（成果全部保留复用），不独立投稿。
- **独立发表重心**：用户选择**游戏设计方向**（非 R7）；方向探索中，见
  `docs/game-design-directions/`。

**R3. 补丁因果效应与十年 meta 演化**
- 做法：先在 5.21→6.1 五个补丁内做 He et al.（FDG 2021）式的因果效应估计（buff 一个英雄如何传导到其他英雄胜率）；若再爬取一份现代（match-v5 可得的近两年）数据，即可做**十年跨度的 meta 演化对比**——这是只有"老数据持有者"能做的研究。
- 目标：FDG / AIIDE / CHI PLAY。

### ⭐ T2：方法升级，有成熟 baseline 可对标

**R4. 带校准与补丁鲁棒性的 draft 胜率预测**
- 做法：在本数据上复现 FM → Transformer（DraftRec 类）谱系，重点不在刷准确率（诚实报告 ~55% 天花板），而在**校准误差、跨补丁泛化、不确定性量化**——这三点是文献自认的缺口。
- 目标：IEEE CoG / IEEE ToG。

**R5. 击杀事件价值建模与实时胜率曲线**
- 做法：用 21.7M 击杀事件 + timeline delta 训练分钟级胜率模型，进而实现 Maymin（JQAS 2021）式的 "smart kills / worthless deaths"——按胜率增量为每次击杀定价，重新给英雄/玩家排名（直接升级原"按次数排名"）。
- 目标：IEEE ToG / Journal of Quantitative Analysis in Sports。

**R6. 英雄表示学习与聚类 2.0**
- 做法：在 kill/assist/co-pick 多重图上学 embedding（OptMatch 式协同/克制双空间，或 GNN），对比官方六大定位与原 k-means 结果；可解释性分析英雄设计空间。
- 目标：IEEE CoG / 作为 R1 的基准任务之一。

### ⭐ T3：空白最大但需要造标签

**R7. 基于遥测的消极行为检测（AFK / 故意送人头）** — *学术空白，但非用户兴趣点（暂缓）*
- 做法：从 timeline 构造弱标签（长时间零输出、异常死亡序列、经济曲线骤停），训练首个学术界公开的行为型 griefing 检测器；Kou 2020 的分类学做理论框架。
- 卖点：三轮文献调研确认学术界几乎空白（仅厂商专利/博客）；可行性已验证（1.3 万名 ≥20 场玩家）。
- 备注：2026-07-15 用户表示更倾向游戏设计方向，R7 暂缓；作为空白储备保留。
- 目标：CHI PLAY / FDG / IEEE ToG。

**R8. 小号/代练检测（原 README 里"Cheating Detection"的现代版）**
- 做法：按 summoner 聚合比赛序列，检测"表现远超当前段位""行为风格突变"的账号。
- 卖点：同样是同行评审空白；风险最高——标签完全缺失，且单赛季窗口限制了序列长度，建议作为 R7 的延伸而非首选。

### ⭐ T4：嫁接 LLM 前沿

**R9. 把数据集变成 LLM 语料/评测集**
- 做法：参照 LoL-MDC 把每场比赛压缩为结构化文本摘要，构建"比赛复盘问答 / 教练建议 / 解说生成"评测基准；也可用于测试 LLM 对时序博弈数据的推理能力。
- 目标：ACL/EMNLP Findings、NeurIPS D&B、或与 R1 合并。

### 支撑性工作（可单独成小文）

**R10. 2016 LoL 数据的分路/角色推断**：把 Demediuk（AIIDE 2019，Dota 2）的方法迁移到 LoL timeline 上，为 R4–R7 提供干净的 role 标签；LoL 至今无权威方案。

---

## 5. 工程前置清单（做任何研究之前）

1. **代码现代化**：统一 Python 3.11+，替换 `pandas.ix`/`as_matrix` 等废弃 API，把爬虫与分析拆成包结构，加测试。
2. **数据验证**：修复击杀事件依赖行序的去重逻辑（用 match_id+happen 主键去重）；核对 Participant 与 Match 数量一致性；统计每个 summoner 的比赛数分布（决定 R7/R8 可行性）。
3. **ETL**：SQLite → Parquet（列式、分 patch/tier 分区），附 schema 文档。
4. **匿名化**：summoner_id/name 哈希化，为公开发布做准备（GDPR / Riot 开发者条款审查）。
5. **诚实记录局限**：单区（NA）、单窗口（预季赛，非正式赛季）、128 英雄、tier 为上赛季段位——这些都应写进数据卡。

---

## 6. 参考文献（经检索核实）

**预测与推荐**
- Semenov et al., *Performance of ML Algorithms in Predicting Game Outcome from Drafts in Dota 2*, AIST 2016
- Kim, Lee, Chung, *A Confidence-Calibrated MOBA Game Winner Predictor*, IEEE CoG 2020, arXiv:2006.15521
- Lee et al., *DraftRec: Personalized Draft Recommendation for Winning in MOBA Games*, WWW 2022, arXiv:2204.12750
- Chen et al., *The Art of Drafting (DraftArtist)*, RecSys 2018, arXiv:1806.10130
- Chen, Zhu, Ye et al., *Which Heroes to Pick? (JueWuDraft)*, IEEE ToG 2021, arXiv:2012.10171
- Hodge et al., *Win Prediction in Multi-Player Esports: Live Professional Match Prediction*, IEEE ToG 2021
- Zhao et al., *Winning Tracker*, WWW 2022; Yang et al., *TSSTN*, arXiv:2008.06313
- Katona et al., *Time to Die*, IEEE CoG 2019, arXiv:1906.03939
- Gong et al., *OptMatch*, KDD 2020; Gu et al., *NeuralAC*, AAAI 2021; Gu et al., *MassNE*, WWW 2023
- Kim, Keegan, Park, Oh, *The Proficiency-Congruency Dilemma*, CHI 2016, arXiv:1512.08321

**图/平衡性/meta**
- Balduzzi et al., *Re-evaluating Evaluation*, NeurIPS 2018, arXiv:1806.02643
- Czarnecki et al., *Real World Games Look Like Spinning Tops*, NeurIPS 2020, arXiv:2004.09468
- He et al., *Heterogeneous Effects of Software Patches in a MOBA Game*, FDG 2021, arXiv:2110.14632
- Zhang & Keegan, *Characterizing Disruptions… Following Software Patches*, arXiv:2207.02736
- Chitayat et al., *Beyond the Meta: Patch-Agnostic Esport Analytics*, AIIDE 2023, arXiv:2305.18477
- Lin et al., *Identifying and Clustering Counter Relationships…*, TMLR 2024, arXiv:2408.17180
- Maymin, *Smart Kills and Worthless Deaths*, J. Quantitative Analysis in Sports 17(1), 2021
- Yang, Harrison, Roberts, *Identifying Patterns in Combat…*, FDG 2014
- Mora-Cantallops & Sicilia, *Player-centric Networks in LoL*, Social Networks 52, 2018

**玩家建模与异常**
- Aung et al., *Predicting Skill Learning in a Large, Longitudinal MOBA Dataset*, IEEE CIG 2018
- Demediuk et al., *Player Retention in LoL: Survival Analysis*, ACSW 2018
- Demediuk et al., *Role Identification for Accurate Analysis in Dota 2*, AIIDE 2019
- Kou, *Toxic Behaviors in Team-Based Competitive Gaming: LoL*, CHI PLAY 2020
- Monge & Matthews, *Blaming the Smurf*, New Media & Society 2025
- Lee et al., *You Are a Game Bot!*, NDSS 2016
- Minka et al., *TrueSkill 2*, MSR TR 2018; Ebtekar & Frans, *Elo-MMR*, WWW 2021
- Weld et al., *CONDA*, Findings of ACL 2021; Naseem et al., *GameTox*, NAACL 2025

**数据集与 LLM**
- Lin et al., *STARDATA*, AIIDE 2017, arXiv:1708.02139
- Białecki et al., *SC2EGSet*, Nature Scientific Data 2023
- Xenopoulos & Silva, *ESTA*, NeurIPS D&B 2022, arXiv:2209.09861
- Kim, Lee, Park, *Structured Summarization of LoL Match Data for LLM Input (LoL-MDC)*, Applied Sciences 15(13), 2025
- Zhang et al., *Game-MUG*, arXiv:2404.19175
- Ma et al., *TextStarCraft II*, arXiv:2312.11865
- Riot API 变更记录与 developer-relations issues #868/#807（match-v4 于 2021-09 废弃、match-v5 历史保留约两年）
