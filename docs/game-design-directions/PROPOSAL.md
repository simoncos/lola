# 研究方案：技能表达与感知失衡——业余玩家如何感知 vs 体验英雄设计

> 工作标题：*Mastery and Mistrust: How Amateur Players Experience vs. Perceive
> Champion Design in League of Legends*
> 方向：游戏设计向实证分析（合并候选 #1 技能表达 + #2 ban 信号）。
> 风格：(a) 面向设计师的实证分析为主，辅以"感知 vs 体验"叙事。
> 决策：2026-07-15，用户确认走 #1+#2 合并方向。

## 一句话贡献

利用一份保存下来的、带**每位玩家段位标签**的 22 万场业余单排数据，量化两件电竞数据
无法回答的设计问题：(1) 每个英雄多大程度上**奖励精通**（性能随玩家段位提升的斜率），
(2) 玩家 ban 的是"真的强"的英雄、还是"感觉不公平"的英雄（ban 率与实测强度的分离）。
两者合起来刻画业余玩家如何**体验**（技能回报）与**感知**（禁用）英雄设计。

## 研究问题

- **RQ1（技能表达）**：每个英雄的性能（胜负贡献、对线经济/经验差、KDA）如何随操作者
  段位变化？据此给英雄的"精通回报 / skill-reward"排名。它与官方"预期难度"标签一致吗？
- **RQ2（感知失衡）**：ban 率与实测强度（段位/位置校正后的胜率与对线表现）差多少？
  存在"被 ban 但不强"的英雄（anti-fun / 感知失衡）与"强但少被 ban"的英雄（sleeper）吗？
- **RQ3（感知 vs 体验的交互）**：高技能表达的英雄（低分段坑、高分段强）是否也更容易在
  高分段被 ban？即"精通回报"是否被读作"不公平"？

## 方法

### 数据与单位
- 单位：英雄 × 段位桶。段位桶合并为 low(Bronze/Silver)、mid(Gold/Plat)、
  high(Diamond/Master/Challenger)，Unranked 单列或剔除（先验证其分布）。
- 性能指标（多个，稳健性交叉验证）：participant_win；对线期 gold/xp/cs per-min delta
  （timeline 前两段）；KDA；damage share。

### RQ1 技能表达
- 每英雄拟合"性能 ~ 段位序数"（混合效应，随机截距=match）得斜率 β_champ = skill-reward。
- **混杂控制（关键）**：不同段位选某英雄的玩家群不同（选择效应）。对策：
  (i) 控制该英雄在各段位的 pick rate；(ii) 用玩家自身跨段位对照（同一 summoner 在
  不同段位的表现——需 summoner 序列，可行性已验证 1.3 万人 ≥20 场）；
  (iii) 报告多指标一致性。
- 外部验证：β_champ 排名 vs Riot 官方难度标签（1/2/3 或 High/Moderate/Low）相关性。

### RQ2 ban 信号
- ban 率 per 英雄 per 段位桶（team_bans + 该场多数段位）。
- 实测强度：段位/位置校正后的胜率（离散选择/条件 logit，因该时代 ban 有位置结构）。
- **感知-实测差** = 标准化 ban 率 − 标准化实测强度。正=感知失衡/anti-fun，负=sleeper。
- 按段位桶看差如何移动（低分段 ban 恐惧 vs 高分段信息充分）。

### RQ3 交互
- 相关 β_champ（skill-reward）与高分段的感知-实测差；检验"高精通回报英雄在高分段更被
  ban"假设。

## 图表清单
- Fig1：英雄性能~段位斜率图（几条代表性英雄 + 全体分布），标注高/低 skill-reward。
- Fig2：ban 率 vs 实测强度散点，四象限（overpowered / anti-fun / sleeper / fair），标注英雄。
- Fig3：感知-实测差随段位桶的变化。
- Fig4：skill-reward vs 高分段感知失衡（RQ3）。
- Table：skill-reward top/bottom 英雄 vs 官方难度标签。

## 与先行工作的划界（详见 ../game-design-directions/README.md）
- 技能表达：只有业界/博客（itero.gg 用熟练度点数非段位）；无同行评审的分段位每英雄
  设计杠杆版本。相邻 PandaSkill（评职业玩家）、Play Style Flexibility（评玩家非英雄）。
- ban 信号：Riot /dev Balance Framework（2019，感知 vs 实际 power）是**引用资产非抢先**；
  学术 ban 工作多为 BP 预测。无分段位感知失衡分解。

## 目标 venue
FDG（设计+分析 track，有 LoL 先例）首选；IEEE ToG / CoG 次之；若叙事偏理论可 CHI PLAY。
与 R1 数据集论文互补，共享 Zenodo DOI。

## P0 原型结果（2026-07-15，`analysis/design_skill_and_bans.py`，真实数据）

**结果通过游戏常识检验的程度很高，是有力开局。**

- **RQ1 技能表达**：最奖励精通的英雄——**猪女(Nidalee)、锴(Kindred)、泰隆、雷恩加尔、
  瑞兹**（公认高操作上限的打野/刺客，低分段坑、高分段强）。最"惩罚"技能的——
  **提莫女(Zyra)、蚂蚱(Amumu)、狼人、纳尔萨斯、火男**（公认低操作、低分段高胜率、
  高分段掉队）。斜率符号与玩家群体认知高度一致。
- **RQ2 感知失衡**：最 anti-fun（狂被 ban 但胜率平庸）——**伊莉丝(Illaoi)、
  탐 켄치(Tahm Kench)、亚索(Yasuo)、德莱厄斯**。**亚索是"因为对面玩着不爽而被 ban、
  但胜率平庸"的教科书案例**——这一条直接坐实了"anti-fun ≠ overpowered"假设，是能让
  设计论文落地的那种 legible finding。象限计数：fair 58 / sleeper 44 / overpowered 18
  / anti-fun 8。sleeper（强但没人 ban）——迦娜、蚂蚱、玛尔扎哈、娑娜（高胜率简单辅助/
  英雄）。
- **RQ3 预览（交互假设已现苗头）**：蚂蚱同时出现在"惩罚技能"底部**和**"sleeper"——
  自洽（简单强力低分段英雄）；锴/雷恩加尔/泰隆同时在"高精通回报"**和**"anti-fun"——
  支持 RQ3 假设（高精通回报英雄在高分段被读作不公平而遭 ban）。

**局限（原型）**：单一胜负指标、无选择混杂校正、ban 无位置模型。P1/P2 补齐。

## 里程碑
- [x] 方向定 + 新颖性检索
- [x] P0 原型：每英雄"性能~段位"斜率 + ban 率 vs 胜率四象限（结果见上，强验证）
- [ ] P1 混杂控制（玩家自身跨段位对照，利用 summoner 序列）+ 多性能指标（对线经济差/KDA）
- [ ] P2 官方难度标签外部验证 + 位置校正的 ban 离散选择模型 + 显著性/CI
- [ ] P3 写作
