# R1 工作计划：LoLA-2016 数据集论文

> 目标：把 2016 Pre-Season 的 22 万场 LoL 比赛档案整理成可公开发布、带基准任务的研究数据集，
> 并撰写数据集论文。核心卖点：Riot match-v4 已废弃（2021-09）、match-v5 仅保留约两年历史，
> **该窗口（patch 5.21–6.1）的 timeline + 击杀事件数据今天已无法从官方渠道重新采集。**

## 里程碑

### M0 — 工具链搭建 ✅（本次提交）
- [x] `lola_dataset/` Python 包：`validate` / `stats` / `export`（含匿名化）三个子命令
- [x] 合成数据库冒烟测试（`tests/make_synthetic_db.py`）
- [x] 数据卡模板（`DATACARD_TEMPLATE.md`）
- [x] 基准任务定义（`BENCHMARKS.md`）

### M1 — 真实数据体检（需要本地的 lola.db）
- [ ] 在本地对 2.1GB 的 `lola.db` 运行：
  ```bash
  pip install -r lola_dataset/requirements.txt
  python -m lola_dataset validate --db lola.db --out reports/validate.json
  python -m lola_dataset stats    --db lola.db --out reports/stats.json
  ```
- [ ] 把两份 JSON 报告提交回仓库（不含任何玩家个人信息，可安全提交）
- [ ] 依据报告确认：击杀事件重复率、Participant/Match 完整性、每个 summoner 的比赛数分布
      （决定 R7/R8 玩家序列研究可行性）

### M2 — 清洗决策（依据 M1 报告定标准并记录在数据卡）
- [ ] 重开局（remake）处理：duration < 300s 的比赛剔除或标注
- [ ] 击杀事件去重：以 (match_id, happen, victim) 为主键（替代旧代码依赖行序的做法）
- [ ] timeline 缺失/残缺比赛的处理策略
- [ ] role/lane 字段噪声评估（2016 API 的 lane/role 公认不可靠 → 引出 R10）

### M3 — 匿名化与发布格式
- [ ] `python -m lola_dataset export --db lola.db --out parquet/ --salt <secret>`
      （summoner_id/name 加盐哈希；`Match.data` 原始 JSON 默认剔除——内含玩家名）
- [ ] 盐值与映射表**永不发布**（保留在本地，用于作者内部纵向研究）
- [ ] 上传 HuggingFace Datasets + Zenodo（拿 DOI），附加载脚本
- [ ] 法务核查：Riot Developer Policies / 数据 ToS；GDPR（玩家名属个人数据 → 全部删除，
      ID 单向哈希）；在数据卡中写明来源与限制

### M4 — 基准任务与 baseline（详见 BENCHMARKS.md）
- [ ] T1 Draft 胜负预测：LR / GBDT / FM / DraftRec-style Transformer；固定按时间切分
- [ ] T2 早期胜率预测（10/20 分钟 timeline 特征）：LR / LightGBM
- [ ] T3 英雄克制结构：matchup 矩阵 + mElo/Nash averaging 分解（与 R2 论文共享代码）
- [ ] 公布标准 train/val/test 划分文件（按 patch 时间顺序切，杜绝时间泄漏）

### M5 — 论文撰写与投稿
- [ ] 数据卡定稿 → 论文正文（结构参照 STARDATA / SC2EGSet / ESTA）
- [ ] 投稿窗口（2026-07 之后）：
  - **Nature Scientific Data**：滚动投稿，最快路径
  - **IEEE DataPort + IEEE ToG dataset 短文**：滚动
  - **AIIDE 2027**（通常 5 月截稿）
  - **NeurIPS 2027 Datasets & Benchmarks**（通常 5–6 月截稿）

## 风险与对策

| 风险 | 对策 |
|---|---|
| Riot ToS 对再分发的限制 | 只发布派生的结构化统计（本身即 API 返回的事实数据），删除原始 JSON blob；参考 Kaggle 上长期存在的同类 LoL 数据集先例；必要时向 Riot 开发者支持提交询问 |
| 玩家隐私（GDPR） | 删除 summoner_name；summoner_id 加盐单向哈希；2016 年 ID 早于 PUUID 且 API 已无法反查，重识别风险极低——仍在数据卡中如实披露 |
| 单区（NA）单窗口（预季赛）的代表性 | 数据卡如实声明为 scope 限制；作为"历史快照"定位而非"通用基准" |
| 22 万场在 2026 年"不够大" | 卖点不是规模而是**不可再生性 + timeline/击杀事件粒度**；引用 OpenDota 2011–2016 转储仍被研究使用的先例 |

## 数据集事实速查（写论文用）

- 222,652 场 Ranked-SOLO-5x5，NA 区，Pre-Season 2016，patch 5.21 / 5.22 / 5.23 / 5.24 / 6.1
- 487,484 summoners；2,226,520 participant 记录（每场 10 人 × 40+ 终局统计）
- 8,906,080 条 ParticipantTimeline（分段 per-min delta：补刀/经济/经验/承伤及对线差值）
- 21,692,852 条 FrameKillEvent（时间、击杀者、被杀者、助攻）
- 1,330,757 条禁用记录；两支队伍的目标数据（大小龙击杀）与胜负
- 玩家 previous-season tier 覆盖 Bronze→Challenger 七档
- 爬取方式：三个种子（Silver/Challenger/Diamond）滚雪球，via Riot API + Cassiopeia（详见 report/）
