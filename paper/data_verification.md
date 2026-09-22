# Data verification record

Cross-check of the scale figures used in the paper against (a) this
repository's pinned export snapshot and (b) the official World Cube Association
(WCA) export pages. Verification performed and re-confirmed on **2026-09-21**.

## Sources

| Source | Location | What it provides |
| --- | --- | --- |
| Snapshot row counts | `data/processed/*.parquet` (Parquet footer metadata) | Exact rows per table for the pinned snapshot |
| Build manifest | `data/processed/manifest.json` | Reconciliation of results / split counts, `frozen_at`, global DNF rate |
| Reconciliation report | `data/processed/reconciliation.json` | `n_results`, train/val/test, `n_assigned`, `n_out_of_window`, `balance_ok` |
| Raw export metadata | `data/raw/metadata.json` | `export_format_version`, `export_date` |
| Official export page | https://www.worldcubeassociation.org/export/results | Format version, changelog, table list, download sizes |
| Official export API | https://www.worldcubeassociation.org/api/v0/export/public | `export_date`, `export_version`, download URLs and **byte sizes** |

## Official export metadata (pulled 2026-09-21)

| 指标 | 官方值 | 来源 URL |
| --- | --- | --- |
| 导出日期 `export_date` | `2026-09-21T00:00:30Z`（readme: September 21, 2026） | https://www.worldcubeassociation.org/api/v0/export/public |
| 导出格式版本 `export_version` | `v2.0.2` | 同上 |
| TSV 压缩包字节数 | **377,258,709** bytes ≈ 359.8 MiB | 同上 |
| SQL 压缩包字节数 | **390,136,209** bytes ≈ 372.1 MiB | 同上 |
| 表清单 | 13 张核心表 + 1 张辅助表（见下） | https://www.worldcubeassociation.org/export/results |
| 联系方式 / 署名 | WCA Results Team | https://www.worldcubeassociation.org/contact?contactRecipient=wrt |

**表清单（13 张核心表）**：`persons`、`competitions`、`events`、`results`、
`result_attempts`、`ranks_single`、`ranks_average`、`round_types`、`formats`、
`countries`、`continents`、`scrambles`、`championships`；
**辅助表**：`eligible_country_iso2s_for_championship`。

**v2.0.2 变更（与 `docs/data/sources.md` 一致）**：`result_attempts` 移除
`id`/`created_at`/`updated_at` 以减小体积；`result_attempts.attempt_number`
改为 unsigned tinyint。

**编码规则（论文已写对，保持不变）**：`-1` = DNF、`-2` = DNS、`0` = 无成绩；
`time` 项目以厘秒为单位（`8653` = 1:26.53）；`number` 项目的 average 以
$100\times$ 均值四舍五入后存储；多盲旧格式 `1SSAATTTTT`、新格式
`0DDTTTTTMM`，最多支持 99 个魔方。

## Snapshot vs. official figures

| 指标 | 本基准快照统计值 (pinned v2.0.2) | 官方页面值/区间 | 来源 URL | 结论 |
| --- | --- | --- | --- | --- |
| Export format version | `v2.0.2` | `v2.0.2` (current) | https://www.worldcubeassociation.org/api/v0/export/public | 一致 |
| Export date | 2026-09-21 00:00:30 UTC (`data/raw/metadata.json`) | 2026-09-21 (`export_date`) | https://www.worldcubeassociation.org/api/v0/export/public | **完全一致** |
| TSV archive size | 377,258,709 bytes（`data/raw/WCA_export_tsv.zip`） | 377,258,709 bytes | https://www.worldcubeassociation.org/api/v0/export/public | **逐字节一致** |
| SQL archive size | n/a | 390,136,209 bytes | https://www.worldcubeassociation.org/api/v0/export/public | 官方量级 |
| results (rows) | **6,909,454** | 未公布行数 | https://www.worldcubeassociation.org/export/results | 快照统计值；官方无对应计数 |
| persons (rows) | **298,551** | 未公布行数 | https://www.worldcubeassociation.org/export/results | 快照统计值；官方无对应计数 |
| competitions (rows) | **18,708** | 未公布行数 | https://www.worldcubeassociation.org/export/results | 快照统计值；官方无对应计数 |
| result_attempts (rows) | **31,847,257** | 未公布行数 | https://www.worldcubeassociation.org/export/results | 快照统计值；官方无对应计数 |
| scrambles (rows) | **3,186,380** | 未公布行数 | https://www.worldcubeassociation.org/export/results | 快照统计值；官方无对应计数 |
| events (rows) | **22**（17 现役 + 已废止；评估中使用 21） | 未公布行数 | https://www.worldcubeassociation.org/export/results | 快照统计值 |
| Train split | 3,211,294 | — | `data/processed/reconciliation.json` | 派生自快照 |
| Validation split | 1,978,851 | — | `data/processed/reconciliation.json` | 派生自快照 |
| Test split | 1,719,290 | — | `data/processed/reconciliation.json` | 派生自快照 |
| Global attempt-level DNF rate | 3.18% (`0.03180194...`) | 未公布 | `data/processed/manifest.json` | 派生自快照 |
| Frozen person–event stats | 612,224 | — | `data/processed/frozen_stats.json` | 派生自快照 |

## Key findings

1. **Export date and format version match the official API exactly**:
   `2026-09-21T00:00:30Z` and `v2.0.2`. This is the strongest possible
   confirmation that the benchmark was built on the current v2 export.
2. **The TSV archive is byte-identical to the official download**: the local
   `data/raw/WCA_export_tsv.zip` is exactly 377,258,709 bytes, matching the
   `tsv_size` returned by the export API. The snapshot is therefore provably the
   official v2.0.2 export of 2026-09-21, not a re-export or a modified copy.
3. **The official pages publish no per-table row counts** — only the format
   version, export date and download byte sizes. The paper's row counts are
   therefore labelled **"this benchmark's snapshot statistics"**, computed from
   Parquet metadata and reproducible from `data/processed/manifest.json`.
4. **Official magnitude is consistent with the snapshot.** A ~377–390 MB archive
   is the right order of magnitude for a database with ~31.8 M attempts and
   ~6.9 M results; no contradiction was found.
5. **The WCA database grows continuously.** Every export carries a new
   sequential version label, so a later download contains more rows than this
   snapshot; the paper notes this in Limitations.

## Actions taken in the paper

* `sections/03_dataset.tex` (and `zh/sections/03_dataset.tex`):
  * table caption now marks all row counts as **snapshot statistics**;
  * added a footnote with the snapshot metadata (format `v2.0.2`, export date
    `2026-09-21`, 14 tables listed but no official row counts);
  * the scale paragraph now names `data/processed/manifest.json`, gives the
    exact official byte sizes, and states that the row counts are not published
    by WCA but are reproducible from the manifest;
  * added `result_attempts` (31,847,257) and `scrambles` (3,186,380) rows and
    corrected `events` to 22.
* `sections/08_limitations_ethics.tex`: extended the "single-snapshot data"
  limitation to state that the export grows continuously and that the scale
  figures are snapshot-specific.
