# LoLA-2016 基准协议 v2（2026-07-20）

> 当前状态：代码已整改，真实数据尚未按 v2 重跑。`benchmarks/output/` 中的旧数值
> 全部撤回，不得引用。每次有效运行必须同时产出结果、split manifest 与 run manifest。

## 共同 cohort 与报告规则

- 排除 `duration < 10` 分钟的比赛；T2 的 20 分钟档额外要求 `duration >= 20`。
- 数据质量必须先通过 `python -m lola_dataset validate --strict`。
- 每个设置均使用互斥 train/val/test；val 选择超参数，选择后在 train+val 上重拟合，
  test 只评估一次。多数类概率只能从 train 估计。
- 报告 Accuracy、AUC、log-loss、ECE；在投稿结论前补 cluster/bootstrap uncertainty。
- Match 没有时间戳；build 顺序与 match_id 仅是时间代理，不得表述为真实时间戳。

### 三个评估设置

1. `temporal-holdout`：早期 build 训练；5.24.0.256 前 20%（match_id 代理顺序）
   验证；其余 5.24.0.256 与 5.24.0.259/6.1.0.484 测试。
2. `iid-mixed-patch`：所有已知 build 混合后按稳定 match_id hash 做 80/10/10。
   这是 IID 控制，不是 same-patch，也不能单独识别 patch 的因果影响。
3. `same-build-5.24.0.256`：只在一个 build 内按稳定 hash 做 80/10/10，提供
   真正的同 build 控制。

所有 build 必须显式列入 `benchmarks/splits.py`；未知 build 直接报错，避免静默泄漏。

## T1 — Draft 胜负预测

- 输入：双方已选英雄的 signed one-hot（蓝 +1，红 -1）。
- 不包含：ban、tier、patch、player history。任何包含这些特征的增强模型必须另命名。
- 基线：训练集 prevalence、正则化逻辑回归、梯度提升。
- 活跃实现：`python -m benchmarks.draft_baseline --parquet <dir>`。

## T2 — 早期局面胜率预测

- 输入：10/20 分钟时的蓝减红团队平均 timeline delta、截至 horizon 的击杀差和一血。
- 不包含：英雄阵容。以免将 T1 与 T2 的贡献混在一起。
- 击杀必须来自规范化后的 `kill_events.parquet`，不能从一助攻一行的原始表重复计数。
- 活跃实现：`python -m benchmarks.early_game_baseline --parquet <dir>`。

## T3 — 阵容交互的增量预测价值

- 主模型：双方英雄主效应的正则化 logistic regression。
- 交互模型：主效应 + anti-symmetric 跨队英雄 pair interaction。
- 任务：在同一 split 上比较 held-out log-loss/AUC，判断交互特征是否增加预测价值。
- 限定解释：单场比赛只有一个团队结果；25 个跨队 pair 不是 25 场独立 head-to-head。
  系数与增量性能都不是因果 counter-pick、lane matchup 或设计平衡证据。
- 活跃实现：`python -m benchmarks.matchup_interaction_baseline --parquet <dir>`。

`analysis/matchup_structure.py` 与 `analysis/matchup_extended.py` 只保留为 legacy
探索性敏感度分析，不属于 v2 T3 的主结论。

## 复现顺序

```bash
python -m lola_dataset validate --db lola.db --out reports/validate-v2.json --strict
python -m lola_dataset export --db lola.db --out parquet-v2 --salt-file SALT_PRIVATE.txt
python -m benchmarks.draft_baseline --parquet parquet-v2
python -m benchmarks.early_game_baseline --parquet parquet-v2
python -m benchmarks.matchup_interaction_baseline --parquet parquet-v2
```
