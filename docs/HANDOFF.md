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

## 六、下一步待办（按优先级）

1. **R2 论文写作**：按 `docs/r2-paper/OUTLINE.md` 起草正文；
   绘制 Fig 2（raw vs corrected 柱状 + 92% 置换基线）与 Fig 3（build 演化）；
   补 HodgeRank（Jiang et al. 2011）引用与校正估计器偏差讨论。
2. **M2 清洗决策定稿**：极短局（<10min，773 场）与 6.1/5.21 小切片的处理写进数据卡。
3. **M3 发布**：Riot Developer Policies 复核 → 许可证定稿（建议 CC BY-NC 4.0
   + Riot 免责句）→ Zenodo 私有草稿 → HuggingFace（域名需加白名单或本地操作）。
4. **M4 扩展**：T2 早期胜率基准（timeline 特征）；FM/Transformer 基线对齐
   DraftRec 设置。
5. **R7 探索**（挂机/送人头弱监督检测）：13,272 名 ≥20 场玩家已确认可行。
6. **数据备份**：确认用户本地留存 lola.zip 与盐值；Release 页补 SHA-256 说明。

## 七、关键文件地图

```
RESEARCH_ROADMAP.md            # 十个研究方向总览（R1–R10）
docs/literature/               # 三份文献综述（引用都核实过）
docs/r1-dataset-paper/         # R1: PLAN / DATACARD / BENCHMARKS / DATA_ACCESS / PUBLISHING
docs/r2-paper/OUTLINE.md       # R2 论文骨架（标题、摘要草稿、图表清单）
docs/HANDOFF.md                # 本文档
lola_dataset/                  # validate / stats / export CLI（python -m lola_dataset）
tests/make_synthetic_db.py     # 合成库冒烟测试
analysis/                      # R2 三个分析脚本 + output/（含 JSON 与 MD 报告）
benchmarks/                    # T1 draft 基准 + output/
reports/                       # 真实库的 M1 体检报告（JSON）
results/                       # 2016 年遗留的派生矩阵（击杀/助攻矩阵等）
report/                        # 2016 年项目报告 PDF
```
