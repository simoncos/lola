# LoLA-2016 Data Card（模板，M1/M2 完成后填充 `TODO` 项）

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
| 比赛 | 222,652 场 Ranked-SOLO-5x5（去重清洗后：TODO） |
| 区服 / 时期 | NA / Pre-Season 2016（patch 5.21, 5.22, 5.23, 5.24, 6.1） |
| 玩家 | 487,484 summoners（匿名化后 ID） |
| Participant 记录 | 2,226,520（40+ 终局统计字段/条） |
| Timeline 记录 | 8,906,080（0-10/10-20/20-30/30-end 四段 per-min delta） |
| 击杀事件 | 21,692,852 原始行（按 (match_id, happen, victim) 去重后：TODO） |
| 禁用记录 | 1,330,757 |
| 英雄数 | 128（2016-01 前的英雄池） |
| tier 覆盖 | Bronze–Challenger（字段为上赛季段位） |

- **每个 patch × tier 的比赛数分布**：TODO（stats 报告生成）
- **比赛时长分布 / remake 比例**：TODO
- **每个 summoner 的比赛数分布**（中位数/分位数）：TODO（决定玩家序列研究可行性）

## Collection Process

- Riot REST API + Cassiopeia wrapper，2016 年采集。
- 滚雪球采样：Silver / Challenger / Diamond 三个种子玩家并行扩展，
  目标 10 万（Silver 种子）+ 6 万（Challenger）+ 6 万（Diamond），最终合并去重。
- **采样偏差声明**：非全量、非均匀抽样；滚雪球方法偏向活跃玩家及其匹配池；
  单区（NA）；预季赛（非正式赛季，玩家动机与正式赛季可能不同）。

## Preprocessing / Cleaning

- 击杀事件按 (match_id, happen, victim) 去重（原始爬虫可能重复写入）：去除 TODO 行。
- duration < 300s 的重开局：TODO 场（标注 `is_remake`，默认剔除出基准任务）。
- 完整性校验结果（Participant=10/场、Team=2/场 等）：TODO。
- 2016 API 的 role/lane 字段噪声较大，按原样保留并在文档中警示（参见 R10 推断方案）。

## Anonymization & Ethics

- `summoner_name` 全部删除；`summoner_id` 加盐 SHA-256 单向哈希（盐值不公开）。
- 原始 `Match.data` JSON blob（内含玩家名）不随数据集发布。
- 2016 年账号 ID 早于 Riot PUUID 迁移，现行 API 无法反查，重识别风险极低。
- 数据为玩家在公开排位系统中产生的比赛事实记录；不含聊天、通信或任何用户生成内容。
- 法务核查记录（Riot Developer Policies / GDPR 评估）：TODO。

## Distribution

- 格式：Parquet（按表组织，Participant/Timeline/KillEvent 附 version 列便于分区过滤）。
- 渠道：HuggingFace Datasets + Zenodo（DOI）：TODO 链接。
- 许可：TODO（建议 CC BY-NC 4.0 + Riot 数据来源声明："isn't endorsed by Riot Games…" 标准免责句）。

## Uses

- 已演示任务：见 BENCHMARKS.md（draft 预测 / 早期胜率 / 克制结构分解）。
- 适合：跨补丁 meta 演化、平衡性度量、弱监督行为检测、LLM 语料构建、教学。
- 不适合：对 2026 年游戏版本的任何直接推断（英雄池/机制已大变）；玩家个体画像。

## Maintenance

- 维护者与联系方式：TODO。
- 勘误机制：GitHub issues（本仓库）。
