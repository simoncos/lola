# Session 交接文档（2026-07-14 ~ 07-15）

> 目的：让新的 session（或协作者）无需读完整个对话即可继续工作。
> 分支：`claude/legacy-project-analysis-qgz7zd`（所有工作已提交于此）。

## 一、项目背景一句话

LoLA 是 2016 年的 LoL 数据分析课程项目（CUHK）；本次将其复活为研究项目：
核心资产是 **222,652 场 NA 排位赛（Pre-Season 2016）的完整档案**，因 Riot API
历史保留政策（match-v4 已废弃、v5 仅存约两年），该数据今天**不可再采集**。

## 二、已完成的工作（按提交顺序）

| 工作 | 产物 | 状态 |
|---|---|---|
| 研究路线图（10 个方向 R1–R10，四个梯队） | `RESEARCH_ROADMAP.md` | ✅ |
| 三方向文献综述（2016–2026，约 70 篇核实引用） | `docs/literature/` | ✅ |
| R1 计划 / 数据卡 / 基准定义 | `docs/r1-dataset-paper/` | ✅ 持续更新 |
| 数据整理工具链（validate / stats / export CLI） | `lola_dataset/` | ✅ 已在真实库验证 |
| 数据获取与发布平台分析 | `DATA_ACCESS.md`、`PUBLISHING.md` | ✅ 决策：Zenodo+HF 双发布 |
| M1 真实数据体检 | `reports/validate.json`、`reports/stats.json` | ✅ |
| M3 匿名化 Parquet 导出（375MB/7 表） | 会话 scratchpad（见下文警告） | ✅ 导出，未发布 |
| R2 分析：击杀代理原型 | `analysis/counter_structure.py` + output | ✅ |
| R2 分析：真实对位 + 噪声校正（核心结果） | `analysis/matchup_structure.py` + output | ✅ |
| R2 分析：build 演化 + bootstrap CI | `analysis/matchup_extended.py` + output | ✅ |
| M4/T1 基准：draft 胜率预测 baseline | `benchmarks/draft_baseline.py` + output | ✅ |
| R2 论文骨架（标题/摘要/结构/图表清单） | `docs/r2-paper/OUTLINE.md` | ✅ v0.1 |
| 新旧分析对应关系 + 分投决策 | `docs/LEGACY_CONNECTIONS.md` | ✅ R1/R2 分投已定 |
| 对抗式新颖性审查（4 路检索） | `docs/literature/04-novelty-check-2026.md` | ✅ R2 定位需调整（见下） |

## 三、核心研究结论（论文素材）

1. **数据质量**：完整性零异常；击杀事件原始重复率 39.5%（键去重后 13,127,488 条）；
   duration 单位为**分钟**；补丁分布不均（5.24 占 58%，6.1 仅 1,298 场）；
   Match 表无时间戳（用 build 版本 + match_id 序作时间代理）。
2. **方法学发现（R2 最大卖点）**：朴素 HodgeRank/mElo 的"循环克制占比"是
   样本量伪影——match 级置换零假设下纯噪声也呈现 ~92% "循环"。
3. **主结果**：扣除置换零假设能量后，真实克制结构仅占对位信号的 **~5%**
   （总体 5.0%；分段位 3.6–6.0%；分补丁 3.6–4.4%——高度稳定）。
   独立的击杀代理分析给出同量级（7.6%）。
4. **外部效度**：对位强度 Top10 与 2016 胜率榜逐名一致（好运姐/迦娜/蒙多…）；
   最强克制对通过玩家常识检验（奥拉夫>德莱厄斯、凯南>鳄鱼、劫>维克兹）。
5. **T1 基准**：签名 one-hot + LR 达 54.7%（跨补丁）/ 55.5%（同补丁），
   GBT 略低——与文献 52–58% 天花板一致；跨补丁使 LR 校准误差恶化 ~3 倍
   （ECE 0.006→0.017）。
6. **build 级 meta 演化与 CI**（`analysis/output/matchup_extended.md`）：
   总体校正循环占比 **5.1%，bootstrap 95% CI [3.6%, 7.7%]**；
   相邻 build 评分 Spearman 0.60–0.77（meta 真实移动）；top movers 与补丁史
   吻合（波比重做恰在 5.24.0.256 边界 +0.22）；build 级克制残差相邻相关 ≈ 0
   —— 单 build 样本下克制估计被噪声主导，呼应第 2 条方法学警示。

## 四、⚠️ 易丢失资产（容器回收即消失，接手前先处理）

会话 scratchpad（`/tmp/claude-0/.../scratchpad/`）中，**未入 git**：

| 文件 | 说明 | 应对 |
|---|---|---|
| `lola.db`（3.57GB） | 原始数据库（从 GitHub Release dataset-v0 的 lola.zip 解压） | 可随时从 release 重新下载，无需担心 |
| `parquet_release/`（375MB） | 匿名化导出产物 | 可用工具重新生成（需盐值） |
| `SALT_PRIVATE.txt` | 匿名化盐值 | **用户须自行留存**；若丢失，重新生成盐值再导出即可（哈希 ID 会全部改变，发布前无影响） |

数据获取途径（已验证可用）：GitHub Release
`https://github.com/simoncos/lola/releases/tag/dataset-v0`（lola.zip，1.07GB，
SHA-256 `9b27ef24bd9a...f420` 见 release 页）。

## 五、如何在新 session 中复现全部结果

```bash
pip install -r lola_dataset/requirements.txt scikit-learn scipy
# 1. 取数据
curl -L -o /tmp/lola.zip https://github.com/simoncos/lola/releases/download/dataset-v0/lola.zip
unzip /tmp/lola.zip -d /tmp/           # -> /tmp/lola.db
# 2. 体检（~1.5 分钟）
python -m lola_dataset validate --db /tmp/lola.db --out reports/validate.json
python -m lola_dataset stats    --db /tmp/lola.db --out reports/stats.json
# 3. 匿名化导出（~7 分钟；盐值自定并私存）
python -m lola_dataset export --db /tmp/lola.db --out /tmp/parquet --salt <SECRET>
# 4. R2 分析（~1 分钟 + ~15 分钟）
python analysis/matchup_structure.py --parquet /tmp/parquet
python analysis/matchup_extended.py  --parquet /tmp/parquet --boot-reps 12
# 5. T1 基准（~20 秒）
python benchmarks/draft_baseline.py --parquet /tmp/parquet
```

已知环境坑（本 session 踩过并解决）：
- 远程环境网络白名单拦截 Google Drive / HuggingFace（实测记录见
  `docs/r1-dataset-paper/DATA_ACCESS.md`）；GitHub 可达。
- SQLite 查询若在 join 两侧使用 CAST 会使索引失效（曾导致 2 小时+ 卡死），
  模式：预建带索引的临时表（见 `lola_dataset/validate.py` / `stats.py`）。

## 五点五、⚠️ 新颖性审查的重大结论（2026-07-15）

四路对抗式检索（`docs/literature/04-novelty-check-2026.md`）后：

- **R2 原定位被实质性抢先**：Hodge 传递/循环分解方法归 Hamilton et al. 2024
  （arXiv:2412.14427）+ Strang 2022；"MOBA 非传递小、强度主导"定性结论归
  Chen & Joachims 2016（blade-chest）；MOBA 反制建模归 Lin & Wu 2024/2025。
  R2 幸存创新点收窄为"组合 + 真实历史数据 + 段位/补丁稳定性 + 置换校正工具 +
  第二证据链"。**分析成果全部有效，只是不足以独立撑起顶会新颖性。**
- **✅ 决策已定（用户）**：R2 走**路径 A**——并入 R1 作旗舰演示分析（成果保留复用），
  不独立投稿。独立发表重心：用户选择**游戏设计方向**（非 R7）；具体方向探索中
  （`docs/game-design-directions/`，定向新颖性检索已启动）。
- **R1 措辞须收窄**："不可再生"仅在"分钟级时间线+击杀事件+全段位+22 万场"组合粒度
  上成立（2016 终局统计在 Kaggle 有存档；GPTilt 已对当前版本做类似内容）。
- **R1 最大落地风险**：Riot ToS/再分发许可——审稿人必问，须设 ToS 专节主动应对。

## 六、下一步待办（按优先级）

0. **✅ R2 决策已定：路径 A**（并入 R1）。独立发表重心 = 游戏设计方向（探索中，
   见 `docs/game-design-directions/`）。R7 暂缓（非用户兴趣点，作空白储备保留）。
1. **R1 推进（现为核心主线）**：把 R2 分析写成 R1 的 Uses 章节 + T3 基准；
   措辞收窄（DATACARD 已改）；补 ToS 专节；Riot Developer Policies 复核 →
   许可证（CC BY 4.0 + Riot 免责句）→ Zenodo 私有草稿。
2. **游戏设计论文（独立主线，实证 P0–P2.5 已完成）**：#1+#2 合并——"技能表达 + ban
   感知失衡"。方案见 `docs/game-design-directions/PROPOSAL.md`。脚本：
   `analysis/design_skill_and_bans.py`(P0) / `design_skill_p1.py`(P1) /
   `design_p2.py`(P2) / `design_p2_5.py`(P2.5)，output/design_p*.md。
   **定位已收敛为测量方法论 + 设计分离发现**：
   (1) "技能表达"三种操作化（win-vs-tier / 对线执行放大 / Riot 难度）两两不相关，
       win-vs-tier 被匹配压缩+选择混杂（弱测度）；
   (2) **技能回报 ≠ 机制难度**——可分离设计轴，角色分层后仍成立（核心发现）；
   (3) 感知：anti-fun ≠ overpowered（亚索/伊莉丝/贾克斯/蒙多稳居 anti-fun），
       奖励精通者在高分段弱显著更被 ban（RQ3，Spearman 0.18, CI[0.001,0.34]）。
   分位置技能放大排名 role-fair 可信（mid: Lissandra/Viktor/Azir/LeBlanc…）。
   **下一步 P3 写作**；目标 FDG/IEEE ToG，与 R1 共享 Zenodo DOI。
   Riot 难度标签已获取：`analysis/riot_difficulty_ddragon.csv`（ddragon 1–10，
   21 个 2016 后重做英雄标为低置信）。
3. **M2 清洗决策定稿**：极短局（<10min）与 6.1/5.21 小切片处理写进数据卡。
4. **M4 扩展**：T2 早期胜率基准（timeline 特征）；FM/Transformer 基线对齐 DraftRec。
5. **R7 探索（升为独立发表首选）**：挂机/送人头弱监督检测；13,272 名 ≥20 场玩家已确认可行。
6. **数据备份**：确认用户本地留存 lola.zip 与盐值；Release 页补 SHA-256 说明。

## 七、关键文件地图

```
RESEARCH_ROADMAP.md            # 十个研究方向总览（R1–R10）
docs/literature/               # 三份文献综述（引用都核实过）
docs/r1-dataset-paper/         # R1: PLAN / DATACARD / BENCHMARKS / DATA_ACCESS / PUBLISHING
docs/literature/04-novelty-check-2026.md  # 对抗式新颖性审查（R2 定位、必引先行工作、R1 风险）
docs/r2-paper/OUTLINE.md       # R2 论文骨架 v0.2（已按新颖性审查修订定位）
docs/HANDOFF.md                # 本文档
lola_dataset/                  # validate / stats / export CLI（python -m lola_dataset）
tests/make_synthetic_db.py     # 合成库冒烟测试
analysis/                      # R2 三个分析脚本 + output/（含 JSON 与 MD 报告）
benchmarks/                    # T1 draft 基准 + output/
reports/                       # 真实库的 M1 体检报告（JSON）
results/                       # 2016 年遗留的派生矩阵（击杀/助攻矩阵等）
report/                        # 2016 年项目报告 PDF
```
