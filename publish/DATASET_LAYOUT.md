# WCA-Bench Release Layout

This document is the normative description of what gets published to the Hugging Face Hub
(and, with the same payload, to ModelScope). It defines the directory structure, the
per-file inventory, the two release tiers, and the storage guidance required by the size of
the data.

The layout is produced by:

```bash
python publish/tools/stage_release.py --tier core      # or --tier full
```

which writes to `publish/_staging/dataset/`. Everything under `publish/_staging/` is
disposable and reproducible from `data/processed/`, `data/splits/` and `examples/`.

---

## 1. Directory Structure

```text
<staging>/dataset/                       # == the Hub repository root
├── README.md                            # HF dataset card (from publish/huggingface/README.md)
├── .gitattributes                       # Git LFS rules (from publish/huggingface/.gitattributes)
├── dataset_infos.json                   # per-config features + splits
├── RELEASE_MANIFEST.json                # generated: tier, per-file size + SHA256
├── data/
│   ├── processed/                       # decoded core tables
│   │   ├── persons.parquet
│   │   ├── competitions.parquet
│   │   ├── results.parquet
│   │   ├── person_event_stats.parquet
│   │   ├── events.parquet
│   │   ├── formats.parquet
│   │   ├── round_types.parquet
│   │   ├── countries.parquet
│   │   ├── continents.parquet
│   │   ├── championships.parquet
│   │   ├── frozen_stats.json
│   │   ├── manifest.json
│   │   └── reconciliation.json
│   ├── splits/                          # temporal split indices + frozen stats
│   │   ├── train_ids.parquet
│   │   ├── val_ids.parquet
│   │   ├── test_ids.parquet
│   │   ├── person_history.parquet
│   │   ├── person_event_stats.parquet
│   │   ├── frozen_stats.json
│   │   └── test_time_slices.json
│   └── optional/                        # full tier only
│       ├── result_attempts.parquet
│       └── scrambles.parquet
└── examples/                            # baseline reports + leaderboard
    ├── README.md
    ├── leaderboard.md
    ├── leaderboard.csv
    └── {task}__{model}.json
```

`data/processed/`, `data/splits/` and `examples/` mirror the source repository paths so that
the published artifact can be dropped back into a checkout without renaming anything.

---

## 2. Release Tiers

The full dataset is ~512 MB (uncompressed Parquet). Most consumers only need the core
tables, so the release is split into two tiers. `stage_release.py --tier` selects the tier.

### 2.1 Core tier (default, ~235 MB)

Everything needed to reproduce tasks T1–T5 and the leakage-free evaluation protocol.

| File | Bytes | Size | Rows |
|------|-------|------|------|
| `data/processed/results.parquet` | 113,086,062 | 107.9 MB | 6,909,454 |
| `data/processed/person_event_stats.parquet` | 10,209,846 | 9.7 MB | 612,224 |
| `data/processed/persons.parquet` | 7,497,080 | 7.2 MB | 298,551 |
| `data/processed/competitions.parquet` | 6,994,459 | 6.7 MB | 18,708 |
| `data/processed/frozen_stats.json` | 9,550,374 | 9.1 MB | — |
| `data/processed/championships.parquet` | 16,816 | 16 KB | 938 |
| `data/processed/countries.parquet` | 8,378 | 8 KB | 207 |
| `data/processed/formats.parquet` | 4,691 | 5 KB | 7 |
| `data/processed/round_types.parquet` | 3,465 | 3 KB | 11 |
| `data/processed/events.parquet` | 3,193 | 3 KB | 22 |
| `data/processed/continents.parquet` | 2,357 | 2 KB | 7 |
| `data/processed/manifest.json` | 1,273 | 1 KB | — |
| `data/processed/reconciliation.json` | 169 | 169 B | — |
| `data/splits/person_history.parquet` | 49,326,572 | 47.0 MB | 6,909,454 |
| `data/splits/train_ids.parquet` | 13,812,389 | 13.2 MB | 3,211,294 |
| `data/splits/person_event_stats.parquet` | 10,209,846 | 9.7 MB | 612,224 |
| `data/splits/frozen_stats.json` | 9,550,374 | 9.1 MB | — |
| `data/splits/val_ids.parquet` | 8,470,737 | 8.1 MB | 1,978,851 |
| `data/splits/test_ids.parquet` | 7,430,599 | 7.1 MB | 1,719,290 |
| `data/splits/test_time_slices.json` | 441 | 441 B | — |
| `examples/*` | < 1 MB | — | — |
| **Core total** | **246,179,121** | **234.8 MB** | — |

> Note: `events`, `formats`, `round_types`, `countries`, `continents` and `championships`
> are tiny but are required to join and decode the main tables, so they are part of the core
> tier even though only a subset was named in the abbreviated task description.

### 2.2 Optional tier (adds ~277 MB)

Per-attempt values and scramble strings. These are large and are only useful for
attempt-level modelling, scramble-conditioned research, or round reconstruction.

| File | Bytes | Size | Rows | Why optional |
|------|-------|------|------|--------------|
| `data/optional/scrambles.parquet` | 146,894,418 | 140.1 MB | 3,186,380 | Only needed for scramble-conditioned work. |
| `data/optional/result_attempts.parquet` | 143,913,699 | 137.3 MB | 31,847,257 | Only needed to rebuild per-attempt sequences / ao5. |
| **Optional total** | **290,808,117** | **277.3 MB** | — | — |

### 2.3 Full tier

`--tier full` = **core + optional = 536,987,238 bytes (512.1 MB)**.

The two tiers are independent upload targets: stage and upload `core` first, then decide
whether to add the optional tables to the same repository (recommended) or a second
repository (`…-attempts`).

---

## 3. Git LFS and Quota Guidance

All Parquet files and the two `frozen_stats.json` files are declared as Git LFS objects in
`publish/huggingface/.gitattributes`:

```gitattributes
*.parquet filter=lfs diff=lfs merge=lfs -text
data/processed/frozen_stats.json filter=lfs diff=lfs merge=lfs -text
data/splits/frozen_stats.json filter=lfs diff=lfs merge=lfs -text
```

- **LFS is mandatory.** Plain Git cannot store 100 MB+ Parquet files; without LFS the push
  will fail or the repository will be unusable.
- **Free-tier quotas** on the Hub (and comparable limits on ModelScope) are on the order of
  a few GB of LFS storage. The full tier stays within a typical free allowance, but repeated
  uploads of large files can exhaust it — prefer one clean push over many re-uploads.
- **Never commit `publish/_staging/` or `publish/dist/`.** They are generated; committing
  them would double the LFS footprint. Add them to `.gitignore` (see `publish/README.md`).

### Sharding recommendations

If a repository needs to stay under a per-file limit, or if consumers should download only a
slice, split the large tables (the staging tool copies files verbatim; sharding is a manual
step before staging):

- **By year** — `scrambles/year=2024/*.parquet` using the competition year. Cleanest for
  time-sliced studies and matches the temporal splits.
- **By event** — `result_attempts/event_id=333/*.parquet`. Best for per-event downloads
  (3x3x3 and 2x2x2 account for most of the volume).
- **By split** — `results/split=train|val|test/*.parquet`. Good when consumers only need the
  test window.

When sharding, update the relevant `configs[].data_files` in `publish/huggingface/README.md`
and the `data_files` globs in `dataset_infos.json` accordingly.

---

## 4. Integrity and Verification

- `RELEASE_MANIFEST.json` (written by `stage_release.py`) records the tier, the exact file
  list, the byte size and the SHA256 of every staged file.
- `publish/tools/make_archive.py` writes `MANIFEST.sha256` (per-file) and `SHA256SUMS`
  (per-archive) alongside the `.tar.gz` / `.zip`.
- To verify a downloaded release:

  ```bash
  sha256sum -c SHA256SUMS              # verify the archive itself
  # then, after extraction:
  sha256sum -c MANIFEST.sha256         # verify every extracted file
  ```

---

## 5. Non-tabular Artifacts

`frozen_stats.json` and `test_time_slices.json` are not tabular and therefore are **not**
declared as loadable configs in `dataset_infos.json`. They describe:

- the world records / skill thresholds frozen at 2022-12-31,
- the global DNF rate,
- the exact `train`/`val`/`test`/`test_a`/`test_b`/`test_c` date boundaries.

Consumers must load them directly with `json.load` and reuse them verbatim; recomputing them
from the test data would introduce temporal leakage.
