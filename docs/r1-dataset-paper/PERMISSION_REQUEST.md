# Riot 许可申请函（正式版，2026-07-16，路径 A 已确认）

> 使用方式：
> 1. 主渠道：https://support-developer.riotgames.com/hc/en-us/requests/new
>    提交工单（分类选 API / Developer Portal 相关；标题用下方 Subject）；
> 2. 同时抄送邮件至 3rdpartyrequests@riotgames.com（API Terms 中指定的联系地址）；
> 3. 发送前把 [方括号] 占位符替换为实际信息；
> 4. 等待期 4–6 周；期间 Zenodo 仅建私有草稿，论文写作照常。
> 一旦有回复（准/驳/附条件），把原文归档到本目录并更新 COMPLIANCE_REVIEW §6。

---

**Subject:** Permission request: publishing a pseudonymized 2016 League of Legends research dataset (non-commercial, academic)

Dear Riot Developer Relations team,

I am writing to request permission — or your requirements — for publishing a
historical League of Legends dataset for non-commercial academic research.

**What the data is.** In late 2015 / early 2016, as part of a university course
project at The Chinese University of Hong Kong, our team collected
approximately 222,000 North American ranked solo-queue matches (patches
5.21–6.1, Pre-Season 2016) through the official Riot Games API using a
personal development key, in accordance with the API Terms in effect at the
time. The archive includes per-participant end-game statistics, per-minute
timeline aggregates, kill events, bans, and players' previous-season tiers.

**Why it matters now.** Since match-v4 was deprecated in 2021 and match-v5
retains roughly two years of history, this patch window can no longer be
re-collected from the API by anyone. The archive has therefore become a unique
historical resource for academic work on game balance, game design, and
machine-learning benchmarks — a snapshot of the game as it was played in 2016,
which we believe also has documentary value for the League community.

**What we would like to publish.** A fully pseudonymized, risk-minimized
version, specifically:

- summoner names removed entirely; summoner IDs replaced by salted one-way
  hashes (salt withheld and never published); raw API JSON excluded;
- hosted on Zenodo (academic archive, DOI) for non-commercial research, with
  a documented takedown / right-to-be-forgotten contact;
- Riot clearly credited as the data source, with your standard disclaimer
  ("[Project] is not endorsed by Riot Games and does not reflect the views or
  opinions of Riot Games or anyone officially involved in producing or
  managing Riot Games properties…");
- our curation code, schema and documentation licensed CC BY-NC 4.0, while
  the dataset terms would state explicitly that the underlying game data
  remains Riot Games' intellectual property and prohibit re-identification
  attempts;
- accompanied by a peer-reviewed dataset paper describing collection,
  quality audit, and limitations.

**Precedent we aim to follow.** For their StarCraft II dataset published in
*Nature Scientific Data* (SC2EGSet, 2023), the authors coordinated with
Blizzard before release. We would like to follow the same good-practice route
with Riot rather than publish unilaterally, and we are happy to: adjust the
data format or fields, add access restrictions (e.g., application-based
access), register the project on the Developer Portal, or meet any other
requirements you consider appropriate.

Could you let us know whether we may proceed with this release, and under what
conditions? I am glad to provide the full field list, our anonymization
procedure, or a private preview of the prepared files.

Thank you very much for your time, and for maintaining the API that made this
work possible in the first place.

Best regards,

[你的姓名]
[职务/身份，如 independent researcher / 原 CUHK 课程项目成员]
[联系邮箱]
Project repository: https://github.com/simoncos/lola
[Developer Portal 账号名，如有]

---

## 工单填写要点

- **分类**：General question / Developer Portal（无对应"数据发布"类目，选最接近的）
- **App/产品名**：LoLA-2016（可注明 "historical research dataset, not a live product"）
- **一句话摘要栏**：Request to publish a pseudonymized 2016 ranked-match
  research dataset (non-commercial, Zenodo, full details inside)
- 若表单问 "does your product serve players"：No — offline academic dataset

## 发送后跟踪

- [ ] 工单已提交（日期：____，工单号：____）
- [ ] 邮件已抄送 3rdpartyrequests@riotgames.com（日期：____）
- [ ] 4–6 周无回复 → 回到 COMPLIANCE_REVIEW §5 在 B/C 间决断
- [ ] 收到回复 → 原文归档本目录 + 更新 COMPLIANCE_REVIEW §6 与 R1 草稿 §3.5
