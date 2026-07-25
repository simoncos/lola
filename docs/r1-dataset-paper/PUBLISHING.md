# 数据集发布平台分析与决策（候选方案，执行延期）

> **2026-07-20：Raw Release 按项目所有者决定延期。** 下文仅比较候选平台，
> 不表示已获许可、已上传、已有 DOI，或当前应执行发布。

对应 PLAN.md 里程碑 M3。结论先行：**Zenodo（存档层）+ HuggingFace（分发层）双发布**。

## 平台对比

| 平台 | DOI | 容量 | 优势 | 劣势 | 结论 |
|---|---|---|---|---|---|
| **Zenodo** | ✅ 自动，含版本化 concept DOI | 50GB/记录（可申请更多） | CERN 运营、欧盟 OpenAIRE 背书的永久存档承诺；GitHub release 联动归档代码；审稿人认可度最高 | 无数据预览、加载不便、ML 社区曝光低 | ✅ 主存档 |
| **HuggingFace Datasets** | ✅ 可选（DataCite，2022 起） | 宽松（LFS/Xet） | `load_dataset()` 一行加载；Dataset Viewer 在线预览；Dataset Card 机制与数据卡对应；ML 社区曝光最高 | 商业公司平台，长期存档无机构背书 | ✅ 主分发 |
| Kaggle Datasets | ❌ | ~100GB | 社区大、notebook 生态、已有 LoL 数据集用户群 | 无 DOI、学术引用弱 | 可选引流 |
| IEEE DataPort | ✅ | 2TB | 与 IEEE 期刊（IEEE ToG）投稿联动 | 访问需 IEEE 账号 | 若投 IEEE ToG 再镜像 |
| OSF | ✅ | 50GB/项目 | 研究项目整体开放（预注册+材料+数据） | 数据集单品曝光一般 | 不选 |
| Figshare | ✅ | 20GB 免费 | 通用、简单 | 与 Zenodo 同质但背书弱 | 不选 |
| Harvard Dataverse | ✅ | 1TB | 机构背书好 | 偏社科社区 | 不选 |
| GitHub Release | ❌ | 2GB/文件 | 方便、与代码同处 | 非存档（可删、无 DOI） | 仅作传输/镜像 |
| Academic Torrents | ❌ | 无限 | 超大数据 P2P | 本数据用不上 | 不选 |

## 双发布方案

1. **Zenodo**：上传匿名化 Parquet + 数据卡 + `lola_dataset/` 工具代码快照
   → 获得 concept DOI；论文引用此 DOI。
2. **HuggingFace**：同一份 Parquet 上传 `datasets` 仓库，Dataset Card 采用
   DATACARD_TEMPLATE.md 内容，页面显著标注 Zenodo DOI 为规范引用。
3. GitHub README 同步指向两处；引用统一收敛到 DOI。
4. 若论文投 IEEE ToG，加镜像 IEEE DataPort。

先例：SC2EGSet = Zenodo + Nature Scientific Data；ESTA = GitHub + NeurIPS D&B
论文；DraftRec 数据集挂在 Google Drive——十年后的今天已属"链接还活着算幸运"，
反证存档层的必要性（本项目自己的 Drive 链接同理）。

## 发布前置条件（硬性）

> **2026-07-16 更新**：条款逐条复核已完成，见
> [COMPLIANCE_REVIEW.md](COMPLIANCE_REVIEW.md)——含最严峻发现（终止即删除条款）、
> 三条路径对比（推荐"先问再发"）、决策清单与可直接使用的申请函稿。
> 措辞修正：对外统一用"假名化（pseudonymized）+ 风险最小化"，不称"匿名"。

- [x] 假名化导出完成并抽查（`python -m lola_dataset export`；玩家名/原始 JSON 已剔除）
- [ ] 许可证定稿：**CC BY-NC 4.0（仅覆盖整理层/schema/工具）** + Riot IP 声明
      + Riot 标准免责声明
      （"LoLA-2016 isn't endorsed by Riot Games and doesn't reflect the views or
      opinions of Riot Games or anyone officially involved in producing or
      managing League of Legends. …"）
- [x] Riot Developer Policies 复核记录归档（COMPLIANCE_REVIEW.md）
- [ ] **向 Riot DevRel 提交许可申请**（路径 A；函稿在 COMPLIANCE_REVIEW 附录，
      需用户发送）；等待期 Zenodo 仅建私有草稿
- [ ] 数据卡 TODO 全部清零（依赖 M1/M2 的真实数据报告）
- [ ] 发布不可逆，以上未全勾选前只建 Zenodo **私有草稿**（draft 状态可反复修改）

## 环境注意

远程研究环境当前无法访问 `huggingface.co`（见 DATA_ACCESS.md 实测表）。
上传发布操作在本地执行，或将 HF 域名加入环境白名单后在会话内执行。
