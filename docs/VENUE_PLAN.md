# 投稿 Venue 分析与方案（2026-07-16）

> 两篇论文（R1 数据集论文 + 设计论文）的会议/期刊选项全量比较。
> 截稿月份基于往年惯例，**投前须核对当年 CFP**。
> 状态：方案已提出，待用户最终确认。

---

## 一、R1 数据集论文《LoLA-2016》

### 期刊选项

| 期刊 | 考量 | 定位 |
|---|---|---|
| **Nature Scientific Data** | 数据集论文的金标准；滚动投稿，审稿约 3–6 个月；SC2EGSet（Nature Sci Data 2023）先例直接可循。**两个硬约束**：(1) APC 约 €2k 级；(2) **要求数据公开托管**——与 Riot 许可直接耦合：获准则完美，被拒则此路基本封死（其受限访问通道主要为生物医学敏感数据设计，游戏数据援引理由较弱） | **许可顺利时的首选** |
| **IEEE Transactions on Games** | 滚动、无强制 APC、games 社区核心期刊；接受 dataset/benchmark 型论文但不如 Sci Data 正统；对数据可用性要求更宽松 | **许可悬置/被拒时的稳健备选** |
| IEEE Access | 快但声誉一般 | 仅保底，不建议 |

### 会议选项

| 会议 | 往年截稿 | 考量 |
|---|---|---|
| **NeurIPS Datasets & Benchmarks** | ~5 月 | ML 社区曝光最大、ESTA 先例；竞争激烈；同样要求数据开放托管 + Croissant 元数据；评审偏好"对 ML 的基准价值"，"历史保存"叙事需强化基准面 |
| **AIIDE**（AAAI） | ~5 月 | STARDATA 先例、games-AI 精准受众、录取压力小于 NeurIPS、论文规格短写作成本低——**会议中性价比最高** |
| FDG | ~1–2 月 | 有 data/analytics track，但作为 R1 归宿稍轻量 |
| IEEE CoG | ~2–3 月 | 同上，更偏分析方法 |

### R1 结论

**视 Riot 许可结果二选一**：顺利 → Scientific Data（持久引用价值 + 正统性）；
悬置/被拒 → IEEE ToG（滚动、不被数据托管要求卡住）。想要 ML 流量且愿等窗口
→ NeurIPS D&B 2027；会议路线首选 AIIDE 2027。

---

## 二、设计论文《Mastery and Mistrust》

### 会议选项

| 会议 | 往年截稿 | 考量 |
|---|---|---|
| **FDG** | ~1–2 月 | 设计+分析的原生场；LoL 实证先例充分（FDG 2025 disengagement、FDG 2021 patch effects）；接受"测量方法论+设计发现"混合贡献；ACM 出版；**时间窗合适**（截稿前足够完成排版+引用核对） |
| **CHI PLAY** | ~2 月 | HCI/玩家体验社区，声誉高于 FDG；"感知 vs 体验"叙事对口；但评审会要求更多玩家视角/理论对话（需补一节与 player experience 文献的衔接）；PACM 形式篇幅要求高 |
| IEEE CoG | ~2–3 月 | 接受度稳，但"设计"味会被稀释成"又一篇 MOBA 分析" |
| AIIDE | ~5 月 | 偏 AI，设计论点非其典型口味 |
| DiGRA | ~1 月 | 偏质性设计理论；我们的定量测量批判在此是异类，除非大改叙事，不建议 |

### 期刊选项

| 期刊 | 考量 |
|---|---|
| **IEEE Transactions on Games** | 滚动；测量类贡献自然归宿（PandaSkill 先例）；篇幅充裕可容纳全部四组实验；缺点=反馈慢于会议 |
| ACM Games: Research and Practice | 新 ACM games 期刊，明确欢迎 research+practice 混合——"给设计师的三轴分离"结论对口；缺点=新刊引用积累浅 |
| Entertainment Computing | 稳妥但影响力一般 |
| ToDIGRA | 同 DiGRA 考量，不建议 |

### 设计论文结论

**首选 FDG 2027**（受众/先例/时间窗三合一）；冲声誉且愿补理论对话 →
CHI PLAY 2027；均不中或求省事 → IEEE ToG 滚动兜底。

---

## 三、跨两篇的时序策略

- 设计论文引用 R1 的 **Zenodo DOI** 即可（R1 挂 DOI 即可引用，不必等见刊），
  两篇理论上可并行。
- 若 Riot 许可在 FDG 截稿（~1–2 月）前未落地：设计论文的数据可用性声明写
  "available upon permission/publication"——FDG 对此宽容，无碍。
- **R1 投 Scientific Data 必须等许可明确**（数据公开托管是硬要求）。
- 因此时序方案：**设计论文按 FDG 2027 时间表推进（不等 Riot）；R1 视许可
  信号在 Scientific Data 与 IEEE ToG 之间二选一后再定模板排版**。

## 四、确认与执行清单

- [ ] 用户确认方案：设计论文 → FDG 2027；R1 → Sci Data / ToG 视许可二选一
- [ ] 确认后：设计论文按 FDG（ACM 格式）LaTeX 化
- [ ] R1 排版等许可信号（Sci Data 与 ToG 模板差异大，不提前做）
- [ ] 投前核对当年 CFP 的确切截稿日与格式要求
