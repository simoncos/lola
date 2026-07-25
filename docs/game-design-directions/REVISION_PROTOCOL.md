# 游戏设计论文修订协议 v1（2026-07-20）

## 状态

这是一份预注册式分析协议，不含新实证结果。旧 `PAPER_DRAFT.md` 的全部数字、英雄
排名、图表和设计结论已经撤回。只有当前脚本重跑并生成 run manifest 后才能写结果。

## RQ1：同一玩家在同一英雄上的观察学习曲线

核心 estimand 是同一 `summoner_id × champion` cell 内，随观察场次增加而发生的
早期对线表现变化，不再用“擅长其他英雄的人是否也擅长 C”的横截面 transfer slope
代替 mastery。

- cohort：比赛至少持续 20 分钟，且两个 early segment 的 CS/XP 差均非缺失；每个
  player-champion cell 至少 5 场。缺失值不按 0 插补。
- 顺序：build 语义顺序 + match_id 升序。由于原 schema 无 timestamp，这只是时间代理。
- outcome：0–20 分钟 CS 差与 XP 差之和，在 `build × position` 内标准化。
- model：cell 内中心化的 `lane_z ~ log(observed_game_number)`，再按 champion 汇总。
- uncertainty：以 player-champion cell 为 cluster 的 bootstrap；至少 200 次，默认 1000。
- 限定：外部比赛不可见、继续使用英雄具有选择性，所以是描述性学习曲线，不是因果
  学习效应，也不等同于机制难度或完整的 teamfight/macro mastery。
- 实现：`python -m analysis.mastery_learning --parquet <dir>`。

旧 `design_skill_p1.py` 与修复后的 `design_p2_5.py` 仅作为 general-skill transfer
敏感度分析，不再支撑 mastery 主张。

## RQ2：相对实测胜率的 ban salience

核心指标为 tier bucket 内 `z(ban rate) - z(observed win rate)`，命名为
`ban-win salience residual`。

- tier bucket：至少 6 名有段位参与者，且 low/mid/high 中存在唯一 plurality；否则不分桶。
- ban：按 `match_id × champion` 去重，并排除空 ban sentinel。
- win：同 bucket 的 champion pick observed win rate。
- uncertainty：英雄层 bootstrap；跨 tier 只报告描述性 rank stability。
- 限定：该 residual 可能同时包含强度、知名度、主播影响、策略、队友偏好与挫败感。
  没有问卷或实验时，不得称为 anti-fun、unfairness、perceived power 或动机证据。
- 实现：`python -m analysis.design_p2 --parquet <dir>`。

## RQ3：学习曲线与 ban salience 的关系

将 RQ1 的 learning slope 与 high-tier salience residual 做 champion-level Spearman
及 bootstrap，仅报告探索性关联。禁止用“mastery 让英雄显得不公平”这样的方向性或
因果措辞。样本量、多重比较与 position 异质性须在结果中完整报告。

## 结果写作闸门

1. strict validation 与规范化 export 通过；
2. `mastery_learning.run.json`、`design_ban_salience.run.json` 存在且 input hash 对应
   同一 Parquet bundle；
3. `analysis/make_figures.py` 从当前 CSV 动态计算图中统计量，无硬编码 CI；
4. 至少一名独立审稿人检查构念效度、选择偏差、bootstrap unit 与过度解释；
5. 摘要与结论只能复述新产物支持的内容，不能搬回旧英雄案例。
