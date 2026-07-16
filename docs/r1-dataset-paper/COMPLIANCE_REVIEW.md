# LoLA-2016 发布合规复核（2026-07-16）

> **性质声明**：本文档是结构化的条款复核材料与决策清单，供项目所有者判断，
> **不构成法律意见**。条款文本证据分三级标注：【全文镜像·逐字】【官方页快照
> 片段级】【社区镜像·近逐字】。本环境无法访问 riotgames.com 官方页面，
> **定稿/行动前须由人对照在线原文复核**（URL 见文末）。

## 一、结论先行

1. **保守解读下，单方面公开发布与条款存在实质张力**——不只是再分发条款，
   还包括一条此前未预见的**终止即删除义务**（见 §2.3，最严峻发现）。
2. **社区实践与执法历史站在另一边**：大规模未获授权的先例长期存在且未被追究
   （Kaggle 2017 年 18 万场数据集在线约 9 年；GPTilt 1000 万场，2024–25）；
   Riot 自己在 2015/2016 年也为 API Challenge 公开分发过批量比赛数据；
   未检索到任何针对数据集/统计站数据再分发的下架或执法记录。
3. **推荐路径：先问再发（ask-first）**——成本低（一张 DevRel 工单），符合
   Scientific Data 的规范先例（SC2EGSet 发布前联系了 Blizzard 并写进论文），
   并把 R1 最大的审稿风险直接转化为优势。详见 §5。

## 二、条款逐条对照（我们的方案 vs 条文）

约束文本 = Riot API Terms and Conditions（"LAST UPDATED: DECEMBER 9, 2013"——
**2016 年采集时与今天的 developer.riotgames.com/terms 是同一份文档**，
经全文 GitHub 镜像与在线页片段逐字比对确认）+ Developer General Policies。

### 2.1 再分发【全文镜像·逐字】——❌ 直接张力

> "Distributing, selling, transferring, encumbering, sublicensing, renting,
> loaning, lending or leasing the Riot Games API, any component thereof,
> and/or access thereto to any third party."
> "Using the Riot Games API to use, distribute or transmit the Game
> Information in any manner not authorized under these API Terms."

许可授权本身是**面向展示**的（"for the purpose of displaying such Game
Information to end users"）。公开数据集不属于被授权的使用方式。
另：现行 General Policies 有 "No apps serving as a 'data broker'" 条款
【片段级】，方向一致。

### 2.2 所有权与二次许可【全文镜像·逐字】——❌ 影响许可证选择

> "…Riot owns all right, title and interest (including all intellectual
> property rights) in and to the Materials… these API Terms do not grant to
> You any right, title, or interest in… the Game and any Game Information."

**含义**：我们无权基于 API 许可对 Game Information 本身施加 CC 许可。
可行做法（社区通行、GPTilt 同款）：对**我们的整理/schema/工具**声明许可，
数据本体注明 Riot 所有 + 标准免责句。原计划的 CC BY 4.0 建议改为
**CC BY-NC 4.0**（与 GPTilt 一致；NC 降低商业化摩擦面）。

### 2.3 终止即删除【全文镜像·逐字】——⚠️ 最严峻发现（此前未预见）

> "Upon termination of these API Terms, You shall immediately cease using the
> Materials, including without limitation any Game Information in Your
> possession, as well as delete all of the Game Information in Your possession."

2016 年的个人 API key 早已失效；保守解读=许可已终止 → 对留存的 Game
Information 存在合同上的删除义务。**这挑战的不只是"能否发布"，而是"能否
留存"**——也正因此，"先问再发"不仅是礼貌，而是把留存本身正当化的最稳途径。
（对抗解读：条款列举的终止触发方式是违约/公告/通知/禁用四种，key 自然过期
是否构成"termination"有争辩空间；此判断超出本复核范围。）

### 2.4 "不得修改或遮蔽"【全文镜像·逐字】——⚠️ 与匿名化的字面张力

> "You shall not modify or obscure any aspect of the Game Information that
> You choose to display."

条文语境是"展示"，但加盐哈希 ID 字面上就是 modify/obscure。抗辩逻辑：
匿名化是隐私保护要求（Riot 自身的 GDPR 义务方向一致），且我们不"展示"原始
字段。仍应在申请函中主动说明匿名化方案，让 Riot 知情。

### 2.5 个人数据类政策【片段级/社区镜像】——✅ 匿名化后基本不触碰

"No personal profiles, scouting tools, guides based on individual players,
or personalized data of any kind, unless an individual player chooses to
share their data."（VALORANT 政策原文；LoL 同向政策见社区镜像。）
匿名化聚合数据集不构成个人档案/侦察工具；但**发布哈希后的每人级序列**
仍应在数据卡中说明用途限制（禁止试图重识别）。

### 2.6 研究/学术条款——**不存在**

条款与政策中既无研究豁免、也无点名禁止；学术用途完全未被规定。
这正是需要主动询问的原因。

### 2.7 必需的免责声明【社区镜像·逐字】——✅ 已计划，措辞照抄

> "[Your Product Name] is not endorsed by Riot Games and does not reflect the
> views or opinions of Riot Games or anyone officially involved in producing
> or managing Riot Games properties. Riot Games and all associated properties
> are trademarks or registered trademarks of Riot Games, Inc"

## 三、GDPR 定性——措辞需要修正

- **加盐哈希 = 假名化（pseudonymized），不是匿名化（anonymized）**：
  只要任何一方（含 Riot）理论上可重链接，即仍属个人数据。EDPB 三测试：
  singling-out / linkability / inference。阵容+时间戳组合对照公开对局史
  常可重识别——不过本数据集的源数据 Riot 侧已过期删除、ID 早于 PUUID，
  实际可链接性显著低于一般情形。**论文与数据卡应使用"假名化+风险最小化"
  的准确表述，不宣称"完全匿名"**。
- **RTBF 机制不兼容**：Riot 的删除请求走"向活跃开发者滚动分发标识符列表"
  机制；冻结的公开数据集无法履行。缓解=提供 takedown/RTBF 联系方式并承诺
  响应（已计划）；在申请函中说明。
- **先例的处理方式**：SC2EGSet（Nature Scientific Data）依赖"源数据本已公开
  + 平台专用许可 + 发布前联系 Blizzard"，未做 GDPR 逐条分析——ask-first 路径
  正是复制这个模板。

## 四、先例与执法态势（对我们有利的一面）

| 先例 | 规模/时间 | 许可声明 | 状态 |
|---|---|---|---|
| Kaggle paololol | 18 万+场，2017 起 | 无明确许可 | **在线约 9 年未被下架** |
| GPTilt (HuggingFace) | 1000 万+场，2024–25 | 自我声明 CC BY-NC 4.0 + 免责句 | 在线 |
| PandaSkill (IEEE DataPort) | 3.7 万职业场 | 未见许可声明 | 在线 |
| Riot 官方 API Challenge | 2015/2016 官方分发批量比赛数据 | — | Riot 自身先例 |

未检索到任何针对数据集/统计站数据再分发的执法记录（执法集中于作弊工具与
客户端内商业化纠纷）；Riot 的实际手段是 key 吊销/产品除名而非诉讼。
【以上均为片段级证据，行动前建议独立复核】

## 五、三条路径与推荐

| 路径 | 内容 | 优劣 |
|---|---|---|
| **A. 先问再发（推荐）** | 经 DevRel 工单 + 3rdpartyrequests@riotgames.com 提交申请（函稿见附录），获回复前 Zenodo 仅建**私有草稿** | 成本=一张工单；获准则一切风险清零且论文可写"with Riot's knowledge"（SC2EGSet 模板）；被拒则明确知道边界；不回复（常见）则转 B 或 C，且已留下善意记录 |
| B. 社区先例路径 | 直接发布：CC BY-NC 4.0（仅限我们的整理层）+ Riot IP 声明 + 免责句 + takedown 联系方式 | 与 Kaggle/GPTilt 同等地位、9 年零执法史；但 §2.1/2.3 的合同张力自担，审稿人可能追问 |
| C. 受限访问 | Zenodo restricted access（申请-批准制）或仅发布聚合统计 | 最保守；数据集论文价值打折 |

**推荐 A，同时并行推进论文写作**（写作不依赖发布状态；投稿时数据可为
"available upon publication / restricted until permission resolved"）。
等待期建议 4–6 周，无回复则由用户在 B/C 间决断。

## 六、决策清单（需项目所有者逐项确认）

- [x] 选定路径：**A（先问再发）**——2026-07-16 用户确认
- [ ] 发送申请：正式函稿与工单填写要点见
      [PERMISSION_REQUEST.md](PERMISSION_REQUEST.md)（**需用户替换占位符后发送**；
      渠道：DevRel 工单 support-developer.riotgames.com/hc/en-us/requests/new，
      抄送 3rdpartyrequests@riotgames.com）
- [ ] 许可证从 CC BY 4.0 改为 **CC BY-NC 4.0（仅覆盖整理层/schema/工具）**
      + Riot IP 声明 + 标准免责句（§2.7 措辞照抄）
- [ ] 论文与数据卡措辞：**"pseudonymized + risk-minimized"** 替代 "anonymized"；
      写明 takedown/RTBF 联系方式与响应承诺
- [ ] 行动前由人对照在线原文复核 /terms 与 /policies/general（本环境无法访问）
- [ ] 数据卡"用途限制"补一句：禁止重识别尝试

## 附录：许可申请函稿（英文，可直接用于 DevRel 工单）

> Subject: Permission request — releasing an anonymized 2016 research dataset
>
> Hello Developer Relations,
>
> In 2016, as part of a university course project (CUHK), we collected
> ~220,000 NA ranked solo-queue matches (patches 5.21–6.1) via the Riot API
> under a personal development key, including match timelines and kill events.
> Because match-v4 has since been deprecated and match-v5 retains ~2 years,
> this window can no longer be re-collected — the archive has become uniquely
> valuable for academic research (game balance, game design, ML benchmarks).
>
> We would like to publish a fully pseudonymized version for non-commercial
> academic research (summoner names removed, IDs salted-hashed, raw API JSON
> excluded), on Zenodo with a takedown / right-to-be-forgotten contact,
> clearly attributing Riot as the data source with your standard disclaimer,
> and licensing only our curation/schema/tooling (CC BY-NC 4.0) while
> acknowledging Riot's ownership of the underlying game data.
>
> May we have your permission (or your requirements) for this release? We are
> happy to adjust the format, add restrictions, or register the project as
> you see fit. Precedent we aim to follow: the SC2EGSet authors coordinated
> with Blizzard before releasing their StarCraft II dataset in Nature
> Scientific Data.
>
> Thank you for your time.

## 引用源（行动前复核）

- API Terms 全文镜像（2013-12-09 版，与现行 /terms 片段逐字一致）：
  github.com/Kevin-Chant/LoL-ChampionSelectGUI（Riot API Terms and Conditions.txt）
- 官方页（本环境 403，须人工复核）：developer.riotgames.com/terms ·
  developer.riotgames.com/policies/general · support-developer.riotgames.com
- Legal Jibber Jabber：riotgames.com/en/legal（数据问题回指 API Terms，
  不独立授权）
- GDPR/RTBF：riotgames.com/en/DevRel/gdpr-right-to-be-forgotten-compliance
- 先例：huggingface.co/datasets/gptilt/... · kaggle.com/datasets/paololol/... ·
  ieee-dataport.org（PandaSkill）· blog.opendota.com（Valve 对比）·
  SC2EGSet（nature.com/articles/s41597-023-02510-7）
- Riot 官方分发先例：benfradet.github.io（2016 hackathon）
