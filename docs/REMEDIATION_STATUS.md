# 2026-07-21 MoA 审稿整改状态

本文件是当前分支的审稿整改来源真相。`docs/HANDOFF.md` 中 2026-07-16
以前的数字与“已完成”表述仅保留为历史记录，不能作为当前投稿证据。
当前审阅结论与执行顺序另见
[`REVIEW_AND_TODOS.md`](REVIEW_AND_TODOS.md)。

## 当前结论

- **Raw Release 延期**：按项目所有者决定，本轮不修改 GitHub Release、Google
  Drive、Zenodo 或 HuggingFace。公开再分发仍受 Riot 许可与合规决策约束。
- **旧实证结果仍然撤回**：`analysis/output/`、`benchmarks/output/` 中
  2026-07-20 以前的 JSON/Markdown/CSV/图表没有当前 run manifest，且使用了被
  审稿发现有缺陷的口径。不得引用其中的准确率、相关系数、置信区间、循环占比或英雄排名。
- **真实数据重跑已完成，但论文仍未恢复投稿状态**：2026-07-21 使用 GitHub Release
  `dataset-v0` 的 `lola.zip`，在 Python 3.12.13 与锁定依赖环境中完成 strict validate、
  HMAC Parquet v2 导出、T1/T2/T3、learning、ban salience 与 figures。新结果有 run
  manifest；旧稿仍需按新结果重写并完成稳健性与独立复审。

## 2026-07-21 真实数据重跑证据

- Release 资产 `lola.zip`：1,075,407,862 bytes；SHA-256
  `9b27ef24bd9ab27756d066d4f0d14c2c3bc58b63d28e3a0b8c6ef66b7ca2f420`；
  解压后的 `lola.db` 为 3,566,427,136 bytes。SQLite `quick_check` 返回 `ok`。
- strict validate 通过，13 张必需/可选表齐全，质量闸门无错误。核心行数为
  222,652 场比赛、2,226,520 参与者、8,906,080 条时间线、13,127,488 个唯一
  kill event 与 18,923,977 条去重 assist relation。
- Parquet v2 共 8 张表、约 412 MiB；逐文件行数与 SHA-256 均与 `manifest.json`
  一致，validation 报告哈希一致。`summoner_id` 使用截断为 128-bit 的
  HMAC-SHA-256；私钥与原始数据库只保存在被 Git 忽略的 `.local-data/`。
- 完整测试为 `18 passed`。三项基准的 run manifest 输出哈希均匹配；所有 split
  manifest 均无 match 跨 partition 泄漏。
- 本轮在尚未提交的整改 worktree 上运行，因此 manifest 明确记录 `git_dirty: true`，
  并额外记录 Git 状态摘要哈希和可执行源码树内容指纹；不能只用 `git_commit` 复现。

## 新结果的审慎解读

- **T1 阵容主效应较弱**：时间外推逻辑回归 AUC 0.5715，IID mixed-patch AUC
  0.5785，同 build AUC 0.5783。
- **T2 早期状态有明显预测力**：时间外推逻辑回归在 10 分钟 AUC 0.7820，在
  20 分钟 AUC 0.8899；20 分钟口径汇总 0--10 与 10--20 两段，不含阵容特征。
- **T3 不支持显式 pair interaction 增益**：加入 8,128 个跨队英雄交互后，三个
  设置的 test log-loss 分别恶化 0.0037、0.0030、0.0020。这是预测性负结果，不能
  推导因果 counter 不存在。
- **学习曲线不支持正向 mastery 主张**：381,053 场合格 player-champion 观测中，
  123 个英雄没有一个 95% bootstrap 区间严格为正；92 个严格为负，31 个跨零。
  该整体负向模式可能反映 match ID 时间代理、档案外对局、选择/生存偏差或构念问题，
  不能解释为玩家真实地“越玩越差”，也不能用于恢复旧 mastery 结论。
- **ban salience 与学习斜率关联不稳健**：高段位 salience residual 与 learning
  slope 的 Spearman 为 0.1448，95% bootstrap 区间 [-0.0281, 0.3152]。区间跨零，
  且 salience 仍不能解释为 anti-fun、unfairness 或玩家动机。
- 四张当前图已重新生成并完成尺寸、裁切、文字与图例检查；它们只可配合上述限制
  使用，不能替代稳健性分析或论文级解释。

## 已修复

### 数据语义与质量闸门

- 将爬虫的一击多助攻存储模型规范化为 `kill_events`（一行一事件）与
  `kill_assists`（一行一事件—助攻关系）。同一事件键的多行不再误报为重复击杀。
- validator 现在区分事件键、多行事件、冗余行、不同助攻关系、完全重复行与
  冲突 payload，并增加参与者、时间线、禁用、击杀成员关系和基数检查。
- validate 与 export 都以只读方式打开数据库；`--strict` 可作为 CI/发布闸门。
- 导出改为分块 ParquetWriter、暂存目录原子替换、128-bit HMAC-SHA-256
  假名 ID，并记录源文件、输出文件、Git commit、Python 与依赖版本的哈希清单。

### 复现与基准协议

- 新增 `pyproject.toml`、Python 3.12 `uv.lock`、locked CI、合成库单元测试与可选的
  Parquet 端到端测试。
- 所有任务共用 duration cohort；所有划分显式验证互斥、完整和已知 build，并写出
  每场比赛的 split manifest。
- T1 口径与代码统一为“仅双方英雄 signed one-hot”；T2 统一为“团队状态差 +
  击杀差 + 一血，不含阵容”。验证集只用于模型选择，测试集不再参与多数类估计。
- 原“same-patch”实际上混合所有 patch，现准确命名 `iid-mixed-patch`；另增加真正的
  `same-build-5.24.0.256` 控制组。
- T3 改为 held-out 预测比较：英雄主效应 vs 主效应 + 正则化跨队交互。结果只能解释为
  阵容交互的增量预测价值，不能解释为因果 counter 或 lane matchup。

### 研究构念

- 旧 P1 的跨玩家 leave-one-out 斜率降级为 `general-skill transfer`，不再称为
  mastery。新增同玩家—同英雄、按观察场次排序并在 build×position 内标准化的
  learning-curve 分析，使用 player-champion cell bootstrap。
- P2.5 的 baseline 现在真正限定在同一 position 内；它仍是 transfer 而非 mastery。
- `ban_z - win_z` 统一称为 `ban-win salience residual`。它不能证明 anti-fun、
  unfairness、perceived power 或玩家动机。
- 旧 Hodge 脚本保留作历史探索诊断，但代码与输出均声明 25 个 pair row 是同一比赛
  结果的相关视图；默认提高 null/boot 重复数，并指向新 T3。
- 图表脚本不再读取旧 P0/P1/P2 结果，也不再硬编码相关系数或 CI。

## 仍需完成的发布闸门

1. 用新结果重写两篇 paper draft 的结果、讨论、图表与摘要；当前 draft 已标记撤回。
2. 增加重复种子或 bootstrap/cluster uncertainty，并由独立审稿人检查模型收敛、
   稳健性和多重比较。
3. 对学习曲线的整体负向结果做构念诊断、替代时间排序与敏感性分析；在解释清楚前
   不作正向或反向因果学习结论。
4. 逐篇核对引用原文；在未完成之前不主张 novelty 或 publication readiness。
5. Raw Release 在获得明确许可/风险决定后另开一轮执行。
