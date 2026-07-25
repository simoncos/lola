# LoLA-2016 Data Card（模板，M1/M2 完成后填充 `TODO` 项）

> **2026-07-20 状态：待 v2 strict validation / export 重跑。** 旧击杀事件
> “39.5% 重复”解释已撤回；Raw Release 延期。本卡中的历史总体数应在重跑后逐项回填。

参照 [Datasheets for Datasets (Gebru et al., 2021)] 与 SC2EGSet/ESTA 的数据卡结构。

## Motivation

- **For what purpose was the dataset created?**
  2016 年 CUHK 课程研究项目（英雄排名/聚类/推荐/胜负预测）采集；2026 年整理发布，
  因 Riot match-v4 API 废弃（2021-09）与 match-v5 约两年的历史保留窗口，
  该时期（patch 5.21–6.1）含时间线与击杀事件的比赛数据已不可再采集。
- **Who created it?** 原始采集：Feng Chen, Wu Di, Zhao Che（CUHK, 2016）。整理发布：TODO。

## Composition

| 项 | 值 |
|---|---|
| 比赛 | 222,652 场 Ranked-SOLO-5x5 |
| 区服 / 时期 | NA / Pre-Season 2016（patch 5.21, 5.22, 5.23, 5.24, 6.1） |
| 玩家 | 487,484 summoners（假名化后 ID；历史计数待 v2 复核） |
| Participant 记录 | 2,226,520（40+ 终局统计字段/条） |
| Timeline 记录 | 8,906,080（0-10/10-20/20-30/30-end 四段 per-min delta） |
| 击杀事件 | 原表为一击多助攻时的一助攻一行表示；v2 分为事件表与 distinct 助攻关系表，真实计数待重跑 |
| 禁用记录 | 1,330,757 |
| 英雄数 | 128（2016-01 前的英雄池） |
| tier 覆盖 | Bronze–Challenger（字段为上赛季段位；participant 计数：Gold 597k / Silver 523k / Plat 446k / Diamond 341k / Unranked 200k / Bronze 65k / Master 42k / Challenger 13k） |

- **build 版本分布**（2026-07 M1 体检，`reports/validate.json`）：
  5.24.x 共 128,000（58%，四个 build）、5.23.x 51,992、5.22.x 41,355、
  6.1.0.484 仅 1,298、5.21.0.297 仅 8——**补丁分布严重不均**，跨补丁实验以
  5.22→5.24 为主战场，6.1 只够做小样本外推检验。
- **比赛时长**：7–87 **分钟**（duration 列单位为分钟；该时期无重开局机制）。
- **每个 summoner 的比赛数分布**：中位数 2、p90=9、p99=37；
  ≥20 场者 13,272 人、≥50 场者 3,404 人 → 玩家序列研究在此子集可行。
- **完整性**（M1 实测）：孤儿记录 0；每场恰好 10 participants、2 teams、唯一胜者。

## Collection Process

- Riot REST API + Cassiopeia wrapper，2016 年采集。
- 滚雪球采样：Silver / Challenger / Diamond 三个种子玩家并行扩展，
  目标 10 万（Silver 种子）+ 6 万（Challenger）+ 6 万（Diamond），最终合并去重。
- **采样偏差声明**：非全量、非均匀抽样；滚雪球方法偏向活跃玩家及其匹配池；
  单区（NA）；预季赛（非正式赛季，玩家动机与正式赛季可能不同）。

## Preprocessing / Cleaning

- 击杀事件不能仅凭 `(match_id, happen, victim)` 多行判为重复：原爬虫会为每个助攻者
  写一行。v2 export 生成一行一事件的 `kill_events` 与 distinct
  `kill_assists`；validator 另行报告 exact duplicate 与 payload conflict。
- duration < 10 分钟的极短比赛（提前投降/挂机废局）：标注并默认剔除出基准任务
  （具体数量见 stats 报告；该时期无 remake 机制）。
- 完整性校验（M1 实测全部通过）：孤儿记录 0、每场 10 participants / 2 teams / 唯一胜者。
- **Match 表无时间戳列**（2016 schema 局限）：时间顺序以 build 版本 + match_id
  升序（Riot match ID 单调递增）为代理。
- 2016 API 的 role/lane 字段噪声较大，按原样保留并在文档中警示（参见 R10 推断方案）。

## Pseudonymization & Ethics

- `summoner_name` 全部删除；`summoner_id` 使用 HMAC-SHA-256 的 128-bit 截断假名
  （盐值不公开）。这降低风险，但不构成不可逆匿名。
- 原始 `Match.data` JSON blob（内含玩家名）不随数据集发布。
- 2016 年账号 ID 早于 Riot PUUID 迁移，现行 API 无法反查，重识别风险极低。
- 数据为玩家在公开排位系统中产生的比赛事实记录；不含聊天、通信或任何用户生成内容。
- 法务核查记录（Riot Developer Policies / GDPR 评估）：TODO。

### ⚠️ ToS/许可证风险（新颖性审查标记为审稿人必问、最大落地风险）

- Riot API 条款禁止"个人档案/侦察工具/基于个人玩家的数据"，且**不授予批量比赛数据的
  再分发权**。带（哈希）玩家键 + 段位标签的每人级数据与此存在张力。
- 先例参差：GPTilt 发布匿名研究聚合（依赖社区容忍，非明确授权）；Oracle's Elixir 发布
  的是**职业（公众人物、聚合）**数据，法律基础不同——都不是"匿名批量排位数据再分发"的
  干净先例。
- **对策（写入论文 ToS 专节，主动 pre-empt）**：数据于 2016 年在当时 API 条款下采集；
  仅供非商业研究；数据仅做风险最小化假名化；提供 takedown / RTBF 联系方式；若发布
  整理层与 schema，须声明底层为 Riot IP。发布前须完成此核查并归档。

## Distribution（延期）

- 格式候选：Parquet（按表组织，kill event 与 assist relation 规范化）。
- 渠道：未决定；HuggingFace / Zenodo 仅为候选，不存在当前 DOI 声明。
- 状态：按项目所有者决定，Raw Release 稍后处理；须先完成许可/风险决策。
- 许可候选：仅整理层/schema；声明底层游戏数据为 Riot IP、
  附 Riot 标准免责句（"isn't endorsed by Riot Games…"）。

### ⚠️ 不可再生性的精确表述（2026-07-15 新颖性审查后收窄）

- **成立**：Riot match-v4 于 2021-09 从 API 移除；官方保留策略"比赛 2 年、timeline 1 年"
  （2019-08 起），2016 timeline 约 2017 年即过期，早于 match-v5，**无法回采**。
- **须收窄**：2016 年的**终局统计**在 Kaggle（`paololol/league-of-legends-ranked-matches`）
  等社区存档中仍存在。本数据集的**独有性**在于"**分钟级时间线 + 原始击杀事件 + 全段位
  + 22 万场规模**"这一组合粒度。措辞：*"据我们所知，唯一保存下来的、在此组合粒度上的
  2016 排位语料"*，**不得**声称"唯一的 2016 排位数据"。
- **内容组合非首创**：GPTilt（HuggingFace, 2024–25）已对**当前版本、王者段**提供类似组合。
  本数据集定位为"首个**保存下来的历史版本**"，非"首个"。

## Uses

- 计划任务：见 BENCHMARKS.md（draft 预测 / 早期胜率 / 阵容交互增量预测）；旧结果已撤回待重跑。
- 适合：跨补丁 meta 演化、平衡性度量、弱监督行为检测、LLM 语料构建、教学。
- 不适合：对 2026 年游戏版本的任何直接推断（英雄池/机制已大变）；玩家个体画像。

## Maintenance

- 维护者与联系方式：TODO。
- 勘误机制：GitHub issues（本仓库）。
