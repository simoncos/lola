# 新颖性对抗审查（2026-07-15）

> 目的：十年间（2016–2026）相关研究大量涌现，本轮用四路对抗式检索专门"证伪"
> R1/R2 的创新点。结论：**R2 原定位（首次分解 LoL 对位矩阵为传递+循环）被实质
> 性抢先，须重新定位；R1 的不可再生论证成立但须收窄措辞并强化合规。**
>
> 检索方法局限：本环境 WebFetch 被出网策略拦截（多数站点 403），结论基于搜索
> 结果摘要 + arXiv ID / DOI / venue 元数据核实，具体数字（如 blade-chest 的准确率
> 差、Hamilton 的收敛表述）需在正式引用前核对 PDF。

---

## 一、R2：对抗审查结果

### 抢先最严重的两篇（必读、必引、必划界）

**1. Hamilton, Kalenkova & Roughan — "Elo Ratings in the Presence of Intransitivity"**
（arXiv:2412.14427, 2024；接收于 *Electronic Journal of Statistics*；姊妹篇
*PLOS ONE* 2025, doi:10.1371/journal.pone.0338261）
- **抢占了我们的方法**：对斜对称 advantage（log-odds）矩阵做 Hodge 分解，拆成
  强传递部分（STACM，即 gradient）+ 循环部分，并用**两者 Frobenius 范数之比**
  I(P) 度量非传递性——与我们的传递/循环能量分解在思想上等同。
- **还抢占了我们的有限样本警示**："随数据量增大，测得的非传递性趋近真值"
  ——正是我们"小样本夸大循环占比"的论点。
- **幸存缺口**：只在 RPS/象棋/模拟数据上做，从未触及真实 MOBA/LoL；未给任何
  真实游戏的经验百分比；无跨段位/跨补丁分析；**用"随 N 收敛"论证，而非我们的
  比赛级结果置换零假设**。

**2. Chen & Joachims — "Modeling Intransitivity in Matchup and Comparison Data"（blade-chest 模型）**
（WSDM 2016；github.com/csinpi/blade_chest）
- **抢占了我们的实质结论**：在真实 **Dota 2 / StarCraft II** 对位数据上发现
  blade-chest 相比 Bradley-Terry 几乎无提升，"队伍形式平滑了低层非传递性，
  **整体强度才是决定因素**"——这在定性上就是我们的 ~5% 结论，而且是 2016 年的。
- **幸存缺口**：通过**预测准确率差**衡量，而非分解出的**能量占比**（从未说"5% 信号
  是循环的"）；队伍/比赛级而非英雄对位级；无 Hodge、无有限样本框架、无段位/补丁。

### 抢先较重的三篇（必引、可对标/对比）

**3. Lin & Wu — 反制关系聚类 / 在线学习**（arXiv:2408.17180, 2024, TMLR 系；
arXiv:2502.03998, 2025, JSAI）：Bradley-Terry 强度（传递）+ 向量量化"反制类别"
（循环），**在 LoL 数据上评估**（136 英雄 Kaggle 集）。是最接近的 MOBA 反制建模。
幸存缺口：定位是平衡性分析/聚类工具，不报循环**能量占比**，无 Hodge、无噪声校正、
无段位/补丁稳定性。

**4. Strang, Abbott & Thomas — "The Network HHD"**（SIAM Review 2022；arXiv:2011.01825）：
锦标赛/胜负矩阵的离散 Helmholtz-Hodge 分解（传递 gradient + 循环 curl），循环范数
即非传递性度量。**这是我们方法的主数学引用**——若我们的分解是 Hodge 式，必须引它。

**5. Sanjaya, Wang & Yang — "Measuring the Non-Transitivity in Chess"**
（*Algorithms* 15(5):152, 2022；arXiv:2110.11737）：在 10 亿+ 象棋对局上用 Nash 聚类
+ RPS 三元环计数测非传递性，发现**在 1300–1700 Elo 段最高、向高低两端递减**。
**恰好与我们"跨段位稳定"相反**——这个反差是我们可用的正面新颖性钩子（可能因为英雄
对位空间 ≠ 象棋策略空间，或因他们未做有限样本校正）。

### 基础/背景引用（低抢先风险）
- **Balduzzi et al., "Re-evaluating Evaluation"**（NeurIPS 2018）+ Open-ended Learning
  （ICML 2019）：反对称博弈的 Schur 分解、Nash averaging、mElo——games 域传递/循环
  分析的源头，即便早于 2020 也**很可能必须引**。
- **Czarnecki et al., "Spinning Tops"**（NeurIPS 2020）：传递+非传递几何，点名 Dota/SC2
  但作为策略/智能体空间，非真实英雄对位矩阵。动机引用。
- **Vadori & Savani, "Ordinal Potential-based Player Rating"**（AISTATS 2024;
  arXiv:2306.05366）：神经式传递/循环分解，关联 sign-rank。最新学习型分解基线。
- **Bertrand et al., "On the Limitations of Elo"**（AISTATS 2023）：真实游戏主要是
  传递的——概念上支持我们的"循环很小"。
- **配对比较统计新线**：arXiv:2406.11584（2024）与 arXiv:2604.00426（2026）——正交
  传递+循环分解并检验循环是否真实，power 超越经典 Kendall-Smith 检验。
- **El-Yaagoubi et al.**（arXiv:2606.08407, 2026）：脑网络 Hodge 分解 + **置换检验 + FDR**
  判定循环 motif 是否显著——机器层面最接近我们的"置换零假设去噪"。
- **Kendall & Babington Smith（1940）** 一致性系数：循环三元环 vs 随机期望的显著性
  检验——"非传递需对照随机基线"这一点 85 年前就有，**不能声称是我们的新洞见**。
- **Alós-Ferrer, Fehr & Netzer**（2022–23）：行为经济学中区分真实 vs 噪声导致的非传递
  （约 14% 循环无法用任何随机效用噪声解释）。
- **Duan et al.（PAKDD 2017）**：多维非传递低秩模型，用 Street Fighter IV + Dota。

---

## 二、R2 幸存的、可辩护的创新点（收窄后）

1. **首次在真实 LoL 英雄对位矩阵上做 Hodge 传递/循环分解**（Hamilton 只在
   RPS/象棋/模拟上做方法）。
2. **给出真实 MOBA 对位矩阵的循环能量占比数字（~5%）**（Chen-Joachims 2016 定性
   得出但从未作为分解百分比；Lin-Wu 建模但不报占比）。
3. **该占比跨段位、跨补丁稳定**——无先例；且与最接近的象棋工作（Sanjaya，段位依赖、
   中段峰值）**结论相反**，反而锐化了贡献。
4. **噪声校正工具**：保留配对结构的比赛级结果置换零假设 + bootstrap CI，用在斜对称
   胜负矩阵上（Hamilton 用"随 N 收敛"，配对比较新线用模型选择，脑网络用条件置换——
   我们的"结果置换保配对结构"这一具体构造未见）。
5. **第二证据链**：击杀代理分解独立给出 7.6%，与胜负矩阵校正值 5.1% 同量级。

## 三、R2 绝不能声称为新的两点（否则被审稿人当场抢白）
- **log-odds/advantage 矩阵的 Hodge 传递/循环分解 + Frobenius 范数比度量** → 归
  Hamilton 2024/2025 与 Strang 2022。
- **有限样本夸大非传递、需对照零假设** → 归 Kendall 1940 / Alós-Ferrer / Hamilton。
  我们的贡献是**在真实 LoL 数据上具体实现并校正**，不是发现这个道理。

---

## 四、R1：对抗审查结果

- **"不可再生"成立但须收窄**：2016 年的**终局统计**在 Kaggle（`paololol/league-of-legends-
  ranked-matches`, 2014–2016 era, 含 teambans）已有存档。我们独有的是**分钟级时间线 +
  原始击杀事件 + 全段位 + 22 万场规模**这个组合。措辞改为"据我们所知，唯一保存下来的、
  在该组合粒度上的 2016 排位语料"，而非"唯一的 2016 排位数据"。
- **内容组合已非首创**：GPTilt 社区项目（HuggingFace `gptilt/lol-ultimate-events-
  challenger-10m`, 2024–25）已提供"分钟级快照 + 击杀/助攻事件 + Parquet"——但**仅当前
  版本、仅王者段**。定位改为"首个**保存下来的历史版本**"，非"首个"。
- **Riot API 保留政策证据充分**：match-v4 于 2021-09-27 从 API 移除；官方保留策略
  "比赛留 2 年、timeline 留 1 年"（2019-08 起滚动）；developer-relations issue #902
  （2024）显示 v5 数据被提前删至约 1 年；旧网页 Match History/ACS 于 2021-09 永久下线。
  → 2016 timeline 约 2017 年即过期，match-v5 出现前数年，**无法回采**，论证站得住。
- **最大风险：ToS/许可证**（审稿人必问）。Riot API 条款禁止"个人档案/侦察工具/基于
  个人的数据"，且不授予批量比赛数据的再分发权。带（哈希）玩家键 + 段位标签的每人级
  数据与之存在张力。**对策**：论文设 ToS 与来源专节——数据于 2016 年在当时 API 条款下
  采集、仅供非商业研究、完全匿名化、提供 takedown/RTBF 联系方式；聚合/schema 以
  CC BY 4.0 发布并声明底层游戏数据为 Riot IP。
- **GDPR**：summoner name/ID 属个人数据，须不可逆哈希（已做）；文档写明合法性基础
  （研究/正当利益）与无重识别意图；2016 ID 多已失效有利但不豁免。
- **norms 对标 SC2EGSet**（Nature Sci Data 2023）：Datasheet + Data Card + Croissant
  元数据 + Zenodo DOI + 开源加载工具 + 固定 split 基准。

---

## 五、战略结论与建议

**R2 作为面向 IEEE ToG 的独立论文，新颖性已偏薄**：方法归 Hamilton/Strang，定性结论
归 Chen-Joachims，MOBA 反制建模归 Lin-Wu。幸存的是"组合 + 真实 LoL 数据 + 段位/补丁
稳定性 + 噪声校正工具"。据此有三条路（推荐 A+C 组合）：

- **A. 把 R2 降格为 R1 数据集论文的旗舰演示分析**。"首个在保存下来的历史 LoL 语料上、
  分段位/分补丁、带噪声校正的对位结构分解"作为数据集**可用性演示**完全够格，且不必
  独立承担顶会新颖性。R1 的核心新颖性（不可再生的历史数据集）更强、争议更小。
- **B. 若仍要独立 R2**：把贡献彻底转到最未被抢先的部分——(i) 噪声校正**工具**本身
  （置换零假设 + bootstrap，斜对称胜负矩阵）；(ii) 与 Sanjaya 象棋"段位依赖"的正面
  对比（我们"段位稳定"）。定位为"方法+实证短文"，投 IEEE CoG/短文或工作坊，且必须
  正面对标 Hamilton/Lin/Strang。风险：仍可能被评为增量。
- **C. 把独立顶会的野心转向真正空白的方向**：前两轮文献调研已确认 **R7（遥测挂机/送
  人头检测）与 R8（小号/代练检测）在学术界几乎空白**（仅厂商专利/博客）。数据支持
  （1.3 万名 ≥20 场玩家）已确认。头部空间远大于 R2。

**建议**：R2 收进 R1 做演示分析（A），把独立发表的重心移到 R7（C）。这样 R1 更厚实、
R7 吃真正的空白，避免在拥挤的传递/循环赛道上做增量。最终取舍留待用户决定。
