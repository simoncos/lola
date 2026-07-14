# 数据获取与环境访问方案（2026-07-14 实测记录）

## 背景

完整数据集 `lola.db`（2.1GB SQLite）目前唯一副本渠道是 2016 年分享的
Google Drive 链接（见根目录 README）。远程研究环境（Claude Code on the web
沙箱）受出网域名策略限制，实测结果如下。

## 网络连通性实测（2026-07-14）

| 域名 | 结果 | 说明 |
|---|---|---|
| `drive.google.com` | ❌ 网关拒绝 CONNECT（策略拒绝） | gdown / 浏览器均不可行 |
| `drive.usercontent.google.com` | ❌ 同上 | Drive 实际文件流域名 |
| `docs.google.com` | ❌ 同上 | |
| `huggingface.co` | ❌ 同上 | 上传/下载 HF 均需白名单 |
| `www.googleapis.com` | ✅ 可达 | Drive API v3 端点可用（需 API key） |
| `github.com` | ✅ 可达 | |
| `objects.githubusercontent.com` | ✅ 可达 | Release asset 下载走此域名 |
| 绕过代理直连 | ❌ 403 | 沙箱不允许直接出网；**浏览器自动化/computer use 无法绕过**（同一网络路径） |

## 可行方案（按推荐顺序）

### 方案 1：环境白名单（推荐，一劳永逸）
在 claude.ai/code 的环境设置中将以下域名加入允许列表：
`drive.google.com`、`drive.usercontent.google.com`、`docs.google.com`；
若要在远程环境直接操作 HF，再加 `huggingface.co`、`cdn-lfs.huggingface.co`。
然后在会话中 `gdown 1X9B60eUSWarMEG9RS3JHbWDaeNuB48LF` 即可。
文档：https://code.claude.com/docs/en/claude-code-on-the-web

### 方案 2：GitHub Release 中转（无需改设置）
在 `simoncos/lola` 创建 release，将数据集压缩包作为 asset 上传
（单文件 ≤ 2GB；SQLite 压缩后预计 0.5–1GB）。远程环境可直接下载。
副作用是顺便摆脱了"个人网盘作为唯一副本"的单点风险——本来就该做。

### 方案 3：Google Drive API + API key（备选）
`www.googleapis.com` 可达。创建启用 Drive API 的免费 key 后：
`GET https://www.googleapis.com/drive/v3/files/{FILE_ID}?alt=media&key={KEY}`
注意：key 建议限制为 Drive 只读、用后作废（会话中传递有泄露面）。

## 数据备份提醒（与访问同等重要）

Google Drive 个人网盘链接已存活十年属于幸运。无论选哪个访问方案，
应尽快在 ≥2 个独立位置持有副本（本地磁盘 + GitHub Release / Zenodo 私有草稿），
再考虑公开发布（发布决策见 PUBLISHING.md）。

## 在数据到位前可推进的研究

仓库内已有全量数据的派生产物，足以启动部分分析：

- `results/kill_matrix_22k.csv` / `assist_matrix_22k.csv`：128×128 英雄
  击杀/助攻矩阵（击杀总数 12.66M，实为全量爬取数据的产物）
  → **R2 克制结构分解的原型已在其上运行**，见 `analysis/`。
- `results/rank_*.txt|csv`：2016 年的排名输出，作为复现基线。

完整 DB 到位后才能做：按 patch/tier 切片、对位（lane matchup）胜负矩阵、
timeline/玩家序列相关的一切（M1 体检 → M2 清洗 → M3 导出）。
