# 2016 年旧分析与新研究的对应关系

> 记录本项目 2016 年原始工作（report/ 与根目录脚本）如何进入 R1（数据集论文）
> 与 R2（克制结构论文）。写 Related Work / Collection Process 时直接取材于此。
>
> 发表策略（2026-07-15 决定）：**R1 与 R2 分投**——R1 投数据集类 venue
> （Nature Scientific Data / NeurIPS D&B / IEEE DataPort+ToG 短文），
> R2 引用 R1 投方法+实证类 venue（IEEE ToG 首选）。理由：可产出两篇、
> 数据集论文引用寿命长、两篇受众不同。

## 一、2016 年工作清单（出处）

| 模块 | 代码/文档 | 当年结论或困境 |
|---|---|---|
| 数据爬取（三段位种子滚雪球，Riot API + Cassiopeia） | `data_crawl.py`、report §Data Crawling | 22 万场 / 48.7 万玩家 / 2.1GB SQLite |
| SQLite schema 设计（12 表） | `sqlite_schema.sql` | 沿用至今；duration 存分钟、无时间戳列 |
| 击杀/助攻矩阵构建 | `champion_matrix.py` | 依赖数据库行序去重（自留 TODO 隐患） |
| 图中心性英雄排名（eigenvector / PageRank / HITS，多种归一化） | `champion_rank.py`、report §Champion Ability Ranking | "与平均分排名无显著差别"；K'' 上特征向量不稳定、HITS 不收敛 |
| 英雄聚类（k-means / 层次，k=6） | `champion_cluster.py` | 发现"战士表现像射手"等 |
| 英雄推荐（胜率榜 + bibliographic coupling） | `champion_relation.py`、report §Recommendation | 胜率 Top10：好运姐/迦娜/蒙多/火男/巨魔/阿木木/龙龟/蚂蚱/狗熊/琴女 |
| 阵容胜负预测（聚类计数特征 + SVM/RF） | `match_predict.py`、report §Win Prediction | ~50%，报告原话 "impossible to predict result before match happens with such features" |
| 事后统计预测 | report §Win Prediction | ~90%（终局特征） |
| 按 tier × version 切片分析 | schema 预留 avg_tier/version 字段 | 构想未完成（TODO） |
| Cheating Detection | README 计划列表 | 从未开始（2026 文献调研确认至今仍是学术空白 → R7/R8） |

## 二、进入 R1（数据集论文）的部分

| 2016 年工作 | 在 R1 中的角色 |
|---|---|
| 爬虫策略与规模 | **Collection Process 一节的主体**：三段位种子（Silver/Challenger/Diamond）滚雪球、目标配额、合并去重流程按当年报告如实记述；2016 团队 = 数据作者 |
| SQLite schema | Composition 一节的表结构基础；其缺陷成为 R1 的披露项：duration 单位为分钟、无时间戳列（以 build 版本 + match_id 序作时间代理） |
| 行序去重的击杀矩阵 | 质量审计的对照：2026 键去重（39.5% 重复、余 13,127,488 条）与当年矩阵总数 12.66M 相差约 47 万，量化了当年方法的残余误差 |
| 当年"22k"命名的派生矩阵（results/） | 实为全量产物；作为数据集附带的 legacy artifact 保留并在数据卡中澄清命名 |
| 未做完的 tier × version 切片构想 | 转化为 R1 基准划分的设计依据（真实 build 分布驱动） |

R1 相对当年的新增量：不可再生性论证（Riot API 政策变迁）、完整质量审计、
匿名化与合规、基准任务与 baseline 成绩、可复现工具链。

## 三、进入 R2（克制结构论文）的部分

| 2016 年工作 | 在 R2 中的角色 | 升级/解释 |
|---|---|---|
| 中心性排名"与平均分无显著差别" | Related Work 起点案例 + 动机 | HodgeRank 分解解释了原因：那些中心性主要度量击杀**体量**（人气×激进度），而非对位**压制**；本 session 实测二者排名 Spearman 仅 0.04 |
| K'' 特征向量不稳定、HITS 不收敛 | 方法学警示的历史注脚 | 对位矩阵在该样本量下被二项噪声主导（置换零假设"循环占比"~92%），谱方法不稳定是噪声主导的自然结果 |
| 归一化方法之争（按 picks / 按共现） | Method 一节的动机 | 成对交换概率与双向折叠使共现暴露量自动抵消，归一化问题被构造性消解 |
| 击杀矩阵本身 | **独立第二证据链**：击杀代理分解给出 7.6% 循环占比，与胜负矩阵校正值 5.1% (CI [3.6%,7.7%]) 同量级互洽 | `analysis/counter_structure.py` |
| 胜率推荐 Top10 | **外部效度锚点**：HodgeRank 强度评分 Top10 与当年胜率榜逐名一致 | 证明新方法在"强度"维度与直观量吻合，增量全在"克制"维度 |
| 阵容预测 ~50% 与"不可能预测"结论 | Discussion 中被修正的历史结论 | 修正为：可以但上限 ~55%（本 session LR 54.7/55.5%），且上限有结构性解释——克制层只占 ~5%，加性强度主导 |
| tier × version 切片构想 | 论文 5.2/5.3 节（跨段位、跨 build 稳定性）正是该 TODO 的完成 | 校正循环占比跨切片稳定（3.6–6.0%） |

## 四、尚未被两篇论文吸收的旧模块（后续方向）

- **英雄聚类**（k-means/层次）→ R6（embedding/GNN 聚类 2.0）的对照基线
- **bibliographic coupling 推荐** → R4/DraftRec 复现时的可解释基线
- **Cheating Detection 构想** → R7/R8（文献确认仍是空白，最大新颖性储备）
