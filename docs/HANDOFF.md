# Session 交接文档（2026-07-14 ~ 07-16，最终版）

> 目的：让新的 session（或协作者）无需读完整个对话即可继续工作。
> 分支：`claude/legacy-project-analysis-qgz7zd`（所有工作已提交于此，未开 PR）。

## 〇、一段话总结本 session

把 2016 年的 CUHK 课程项目 LoLA 复活为研究项目。核心资产是 **222,652 场 NA 排位赛
（Pre-Season 2016）档案**——因 Riot API 保留政策（match-v4 已废弃、v5 仅存约两年），
其时间线+击杀事件粒度的数据**今天不可再采集**。本 session 完成了：研究路线图与四轮
文献调研（含对抗式新颖性审查）→ 数据获取（GitHub Release 中转）→ 工具链与质量审计
→ 匿名化导出 → 三组分析（对位克制结构 / draft 基准 / 技能表达与 ban 感知）→
**两篇论文完整初稿**（R1 数据集论文 + 游戏设计论文）+ 四张出版级图表。

## 一、最终成果一览（两篇论文 + 支撑）

### 论文 1：LoLA-2016 数据集论文（R1，核心主线）
- **初稿**：`docs/r1-dataset-paper/PAPER_DRAFT.md`（v0，SC2EGSet/ESTA 规范）
- 支撑：`PLAN.md`（里程碑 M0–M5）、`DATACARD_TEMPLATE.md`（已填实测数字）、
  `BENCHMARKS.md`（T1–T3 防泄漏划分）、`DATA_ACCESS.md`、`PUBLISHING.md`
  （Zenodo 存档 + HuggingFace 分发双发布决策）
- 基准成绩已实测：T1 draft 预测 LR 54.7%（跨补丁）/55.5%（同补丁）；
  T3 对位分解（原 R2 全部分析并入，见下）
- 目标 venue：Nature Scientific Data / NeurIPS D&B / AIIDE / IEEE DataPort

### 论文 2：游戏设计论文（用户兴趣主线）
- **初稿**：`docs/game-design-directions/PAPER_DRAFT.md`
  （*Mastery and Mistrust*，v0）+ 4 张图（`analysis/output/figures/`，
  `analysis/make_figures.py` 生成，Okabe-Ito 色盲安全，300dpi）
- 方案与实证记录：`docs/game-design-directions/PROPOSAL.md`（P0–P2.5 全记录）、
  `README.md`（五方向新颖性排序）
- 脚本：`analysis/design_skill_and_bans.py`(P0) → `design_skill_p1.py`(P1)
  → `design_p2.py`(P2) → `design_p2_5.py`(P2.5)；输出 `analysis/output/design_p*.{md,json}`
- 外部数据：`analysis/riot_difficulty_ddragon.csv`（Riot 难度 1–10；21 个 2016 后
  重做英雄标低置信）
- 目标 venue：FDG / IEEE ToG（测量类贡献）

### 已并线：R2 克制结构分析（→ R1 的 T3 基准）
- 用户决策（路径 A）：不独立投稿，并入 R1 作旗舰演示。分析全部完成且有效：
  `analysis/counter_structure.py`（击杀代理）、`matchup_structure.py`（胜负矩阵+
  噪声校正）、`matchup_extended.py`（build 演化+bootstrap CI）
- 独立骨架存档备查：`docs/r2-paper/OUTLINE.md`（v0.2，含"必引先行工作"划界表，
  R1 写 T3 章节时仍要用）

## 二、核心研究结论速查（写论文直接引用）

### 数据质量（R1 素材）
- 完整性零异常（0 孤儿、每场 10 人/2 队/唯一胜者）；与 2016 报告行数完全吻合
- 击杀事件原始重复率 **39.5%**（键去重后 13,127,488 条）；duration 单位为**分钟**；
  Match 表无时间戳（build 版本 + match_id 序作时间代理）；补丁分布不均（5.24 占 58%）
- 蓝方胜率 50.6%、时长峰值 30–35 分钟、击杀峰值 20–25 分钟——全部通过时代常识检验
- 玩家序列可行性：13,272 人 ≥20 场

### 克制结构（R1 的 T3 素材）
- **方法学警示**：朴素 HodgeRank/mElo"循环占比"是样本量伪影——置换零假设下纯噪声
  也呈现 ~92% "循环"
- **主结果**：校正后真实克制仅占对位信号 **5.1%（bootstrap 95% CI [3.6%, 7.7%]）**，
  跨段位（3.6–6.0%）跨补丁（3.6–4.4%）稳定；击杀代理独立给出 7.6%（同量级互洽）
- 外部效度：强度 Top10 与 2016 胜率榜逐名一致；克制对通过常识检验；
  build 级 top movers 与补丁史吻合（波比重做 5.24.0.256 应声 +0.22）

### 技能表达与 ban 感知（设计论文素材）
- **三种"技能表达"操作化两两不相关**（|Spearman| ≤ 0.19）：win-vs-tier（P0）被匹配
  压缩+选择混杂；个体留一法放大（P1）更可信且 face-valid；Riot 难度是第三个构念
- **技能回报 ≠ 机制难度**（核心发现）：角色分层后偏相关仍 −0.03——滚雪球/续航英雄
  （Jax/Cho'Gath）低难度高回报，部分高难度英雄不回报
- **anti-fun ≠ overpowered**：亚索/伊莉丝/贾克斯/蒙多跨段位稳居"被 ban 但不强"；
  sleeper=迦娜/蚂蚱/玛尔扎哈；感知信号跨段位 Spearman 0.58–0.86
- **RQ3**：奖励精通者在高分段弱显著更被 ban（0.18，CI [0.00, 0.34]）；
  锴仅在高分段变 anti-fun 是活例证

### 战略判断（已由用户确认的决策）
- 新颖性对抗审查（`docs/literature/04-novelty-check-2026.md`）：R2 独立定位被
  Hamilton 2024 / Chen-Joachims 2016 / Lin-Wu 2024-25 实质抢先 → **路径 A**（并入 R1）
- R1"不可再生"措辞已收窄至"时间线+击杀事件+全段位+22 万场"组合粒度
- 独立发表重心 = 游戏设计方向（用户兴趣）；R7（行为检测，学术空白）作储备暂缓
- R1 与设计论文**分投**，设计论文引用 R1 的 Zenodo DOI（R1 挂 DOI 即可引用，无需等见刊）

## 三、⚠️ 易丢失资产（容器回收即消失）

会话 scratchpad（`/tmp/claude-0/.../scratchpad/`）中，**未入 git**：

| 文件 | 说明 | 应对 |
|---|---|---|
| `lola.db`（3.57GB） | 原始库（lola.zip 解压） | 可随时从 Release 重下 |
| `parquet_release/`（375MB） | 匿名化导出 | 工具可再生（需盐值） |
| `SALT_PRIVATE.txt` | 匿名化盐值 | **用户自行留存**；丢失则换盐重导（发布前无影响） |

数据获取（已验证）：GitHub Release
`https://github.com/simoncos/lola/releases/tag/dataset-v0`
（lola.zip 1.07GB，SHA-256 `9b27ef24bd9a...f420` 见 release 页）。

## 四、复现全部结果（新 session 照抄即可）

```bash
pip install -r lola_dataset/requirements.txt scikit-learn scipy matplotlib
# 1. 数据
curl -L -o /tmp/lola.zip https://github.com/simoncos/lola/releases/download/dataset-v0/lola.zip
unzip /tmp/lola.zip -d /tmp/                                  # -> /tmp/lola.db
# 2. 体检（~1.5 分钟）
python -m lola_dataset validate --db /tmp/lola.db --out reports/validate.json
python -m lola_dataset stats    --db /tmp/lola.db --out reports/stats.json
# 3. 匿名化导出（~7 分钟；盐值自定并私存）
python -m lola_dataset export --db /tmp/lola.db --out /tmp/parquet --salt <SECRET>
# 4. 克制结构（T3）：~1 分钟 + ~3 分钟 + bootstrap ~15 分钟
python analysis/counter_structure.py
python analysis/matchup_structure.py --parquet /tmp/parquet
python analysis/matchup_extended.py  --parquet /tmp/parquet --boot-reps 12
# 5. T1 基准（~20 秒）
python benchmarks/draft_baseline.py --parquet /tmp/parquet
# 6. 设计论文实证 P0-P2.5（各 ~20-40 秒）
python analysis/design_skill_and_bans.py --parquet /tmp/parquet
python analysis/design_skill_p1.py --parquet /tmp/parquet
python analysis/design_p2.py --parquet /tmp/parquet --difficulty analysis/riot_difficulty_ddragon.csv
python analysis/design_p2_5.py --parquet /tmp/parquet
# 7. 论文图表
python analysis/make_figures.py
```

已知环境坑（本 session 踩过并解决）：
- 远程环境白名单拦截 Google Drive / HuggingFace / ddragon / arXiv 全文
  （实测记录：`docs/r1-dataset-paper/DATA_ACCESS.md`）；GitHub 可达
- SQLite join 两侧 CAST 会废掉索引（曾致 2 小时+ 卡死）；
  解法=预建带索引临时表（见 `lola_dataset/validate.py` / `stats.py`）
- 文献检索：本环境读不到 arXiv 全文，引用细节均为搜索摘要级——**投稿前必须
  精读核对**（尤其 Hamilton 2412.14427、Chen-Joachims WSDM 2016、PandaSkill）

## 五、走向发表的待办（按优先级）

1. **发布合规（R1 的闸门，需用户/本地）**：Riot Developer Policies 复核并归档 →
   许可证定稿（建议：聚合/schema CC BY 4.0 + Riot IP 声明 + 免责句）→
   Zenodo **私有草稿**上传（拿 DOI 但先不公开）→ HuggingFace（需本地或加白名单）
2. **两篇正式排版**：LaTeX + 目标 venue 模板；参考文献格式化并**逐篇核对全文**；
   R1 数据卡 TODO 清零（维护者、DOI 链接）
3. **投稿窗口**：R1 → Scientific Data（滚动）或 NeurIPS D&B 2027 / AIIDE 2027
   （约 5 月截稿）；设计论文 → FDG 2027 / IEEE ToG（滚动）
4. **可选加强**：~~T2 早期胜率基准补跑~~ ✅ 已完成（`benchmarks/early_game_baseline.py`：
   10 分钟 70.9/71.3%、20 分钟 80.3%；**跨补丁惩罚在状态特征上近乎消失**，与 T1 的
   draft 特征形成可引用对比——补丁改变"什么阵容强"，不改变"领先意味着什么"）；
   设计论文 RQ3 的按位置稳健性；R2→T3 章节按 OUTLINE v0.2 划界表落实
5. **数据备份确认**：用户本地留存 lola.zip + 盐值；Release 页描述补 SHA-256
6. **储备方向**（暂缓）：R7 行为检测（学术空白已确认）；R3 十年 meta 演化
   （需补采现代对照数据）

## 六、关键文件地图

```
RESEARCH_ROADMAP.md                       # 十方向总览（含各方向最新状态标注）
docs/HANDOFF.md                           # 本文档
docs/LEGACY_CONNECTIONS.md                # 2016 旧分析 ↔ 新研究对应 + 分投决策
docs/literature/                          # 4 份文献调研（01-03 综述 + 04 新颖性审查）
docs/r1-dataset-paper/                    # 论文1：PAPER_DRAFT + PLAN/DATACARD/BENCHMARKS/
                                          #   DATA_ACCESS/PUBLISHING
docs/game-design-directions/              # 论文2：PAPER_DRAFT + PROPOSAL + 方向调研
docs/r2-paper/OUTLINE.md                  # 已并线的 R2 骨架（T3 划界表仍需用）
lola_dataset/                             # 数据工具链 CLI（validate/stats/export）
tests/make_synthetic_db.py                # 合成库冒烟测试
analysis/                                 # 全部分析脚本 + output/（报告与 figures/）
benchmarks/                               # T1 基准 + output/
reports/                                  # 真实库 M1 体检报告（JSON）
results/                                  # 2016 遗留派生矩阵
report/                                   # 2016 项目报告 PDF
```

## 七、Git 状态

- 分支 `claude/legacy-project-analysis-qgz7zd`，20+ 提交，全部已推送；未开 PR
- 提交轨迹即工作日志：路线图 → 文献 → 工具链 → 体检修复 → 导出与分析 →
  新颖性审查与重定位 → 设计方向实证 → 两篇论文初稿 → 本收尾
