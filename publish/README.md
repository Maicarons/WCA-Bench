# WCA-Bench Publishing Guide

This directory contains everything required to publish WCA-Bench to the **Hugging Face Hub**
and **ModelScope (魔搭)**. Nothing here uploads anything by itself; the upload scripts are
dry-run first and always read credentials from environment variables.

> Status: **prepared, not yet published.** The repository ids below are placeholders
> (`Maicarons/WCA-Bench`) and should be confirmed before a real upload.

---

## 1. Contents

```text
publish/
├── README.md                    # this file
├── DATASET_LAYOUT.md            # normative data layout, tiers, LFS guidance
├── huggingface/
│   ├── README.md                # HF dataset card (English, YAML front matter)
│   ├── .gitattributes           # Git LFS rules
│   ├── dataset_infos.json       # per-config features + splits
│   ├── upload_dataset.py        # create/update the dataset repo and upload
│   ├── upload_models.py         # upload baseline reports as a model repo
│   └── requirements.txt
├── modelscope/
│   ├── README.md                # ModelScope dataset card (English + 中文摘要)
│   ├── configuration.json       # ModelScope dataset/model configuration
│   ├── dataset_meta.json        # name / description / tags / license
│   ├── upload.py                # upload via the modelscope SDK
│   └── requirements.txt
└── tools/
    ├── stage_release.py         # assemble data/processed + data/splits + examples
    ├── verify_release.py        # checksum + A1.2 provenance checks before upload
    └── make_archive.py          # tar.gz / zip archives + SHA256 manifests
```

---

## 2. Pipeline Overview

Both pipelines share the **same payload**, assembled once by the staging tool.

### 2.1 Hugging Face Hub

```text
data/processed + data/splits + examples
        │  publish/tools/stage_release.py --tier core
        ▼
publish/_staging/dataset/   (Hub repository layout)
        │  publish/huggingface/upload_dataset.py
        ▼
https://huggingface.co/datasets/Maicarons/WCA-Bench
```

Optional distributable snapshot:

```text
publish/_staging/  ──►  publish/dist/wca-bench-<name>.tar.gz|.zip + SHA256SUMS
        (publish/tools/make_archive.py)
```

### 2.2 ModelScope

```text
publish/_staging/dataset/   ──►  publish/modelscope/upload.py  ──►  ModelScope repo
```

---

## 3. Preparation Steps

Run from the repository root (`f:/workspace/WCA-Bench` on Windows).

### Step 0 — build the dataset (if not already present)

```bash
python scripts/download_data.py
python scripts/build_dataset.py --source raw
```

This produces `data/processed/` and `data/splits/`. The real export is ~512 MB across the
processed + split artifacts; see `DATASET_LAYOUT.md` for the exact inventory.

The build writes the A1.2 `checksums` section and the A1.4 `average_agreement` fields into
`data/processed/manifest.json`. If you already have built tables but a manifest from an older
version, refresh those fields in place instead of rebuilding:

```bash
set PYTHONPATH=src                 # Windows cmd.exe; use `export PYTHONPATH=src` in bash
python scripts/refresh_manifest.py --dry-run   # preview
python scripts/refresh_manifest.py            # rewrite manifest.json
```

### Step 1 — stage the release

```bash
# Core tier ("~235 MB"): small tables + results + splits + examples
python publish/tools/stage_release.py --tier core

# Full tier (~512 MB): also stage scrambles + result_attempts under data/optional/
python publish/tools/stage_release.py --tier full --clean
```

Output: `publish/_staging/dataset/` plus a `RELEASE_MANIFEST.json` with per-file sizes and
SHA256 digests. Use `--dry-run` to preview without copying.

### Step 1.5 — verify the staged release (do this before every upload)

```bash
python publish/tools/verify_release.py
```

This performs two independent checks and exits non-zero on any mismatch:

1. **Staging self-consistency** — every file listed in `RELEASE_MANIFEST.json` exists and its
   SHA-256 matches what was recorded at staging time.
2. **Provenance against the build manifest** — every staged `data/processed/<table>.parquet`
   matches the SHA-256 recorded in `data/processed/manifest.json`. This guarantees that what is
   uploaded is the artefact the reproducibility tests (A1.2) were actually run against, rather
   than a stale or locally modified copy.

### Step 2a — upload to the Hugging Face Hub

```bash
python -m pip install -r publish/huggingface/requirements.txt

set HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxx          # Windows cmd.exe
# export HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxx     # bash

# Preview first — no network requests
python publish/huggingface/upload_dataset.py --dry-run

# Real upload (public by default)
python publish/huggingface/upload_dataset.py --repo-id Maicarons/WCA-Bench --public
```

Baseline reports (the `examples/` directory) can be published separately as a model repo:

```bash
python publish/huggingface/upload_models.py --dry-run
python publish/huggingface/upload_models.py --repo-id Maicarons/WCA-Bench-baselines
```

### Step 2b — upload to ModelScope

```bash
python -m pip install -r publish/modelscope/requirements.txt

set MODELSCOPE_API_TOKEN=ms-xxxxxxxxxxxxxxxx      # Windows cmd.exe
# export MODELSCOPE_API_TOKEN=ms-xxxxxxxxxxxxxxxx # bash

python publish/modelscope/upload.py --dry-run
python publish/modelscope/upload.py --repo-id Maicarons/WCA-Bench --repo-type dataset
```

### Step 3 — optionally build a distributable archive

```bash
python publish/tools/make_archive.py --dry-run
python publish/tools/make_archive.py --name core --format both
# -> publish/dist/wca-bench-core.tar.gz, .zip, MANIFEST.sha256, SHA256SUMS
```

---

## 4. Credentials and Safety

- **Tokens are never written to disk.** Every upload script reads its token from an
  environment variable: `HF_TOKEN` for the Hub, `MODELSCOPE_API_TOKEN` for ModelScope. If the
  variable is missing, the script refuses to upload and exits non-zero.
- **Dry-run everywhere.** All four scripts support `--dry-run`, which prints the exact file
  list (with sizes) and the intended repository operations, and makes **no** network calls.
- **Graceful dependency handling.** If `huggingface_hub` or `modelscope` is not installed,
  the script prints the matching `pip install` command and exits non-zero instead of raising
  a traceback.
- **Private by default is available.** Both uploaders accept `--private` / `--public`; the
  default is public, matching the planned open release.

---

## 5. Notes and Recommendations

### 5.1 Suggested `.gitignore` additions (do **not** apply to the root `.gitignore` automatically)

The staging and archive directories are generated and can be hundreds of MB. It is
recommended that the maintainers add the following lines to the repository `.gitignore`:

```gitignore
# publish (generated artifacts)
publish/_staging/
publish/dist/
```

This guide intentionally does not modify the root `.gitignore`; the change is left to the
maintainers.

### 5.2 Licensing and attribution

- **Code:** Apache-2.0.
- **Data:** owned by the World Cube Association, redistributed under the WCA public export
  terms. The dataset card reproduces the required attribution verbatim:

  > This information is based on competition results owned and maintained by the
  > World Cube Association, published at https://worldcubeassociation.org/results

- The Hub dataset card uses `license: other` with `license_name: wca-export-terms` because
  the WCA export terms are not an SPDX identifier. Confirm this is acceptable before the
  public release if a stricter SPDX-looking value is required.

### 5.3 Large-file discipline

- `*.parquet` and the two `frozen_stats.json` files are uploaded through **Git LFS**
  (`publish/huggingface/.gitattributes`). Do not remove those rules.
- Prefer a single upload over repeated large pushes to conserve LFS quota. See
  `DATASET_LAYOUT.md § 3` for sharding strategies (by year / event / split).

### 5.4 Open decisions before publishing

1. **Repo id** — `Maicarons/WCA-Bench` is a placeholder; replace with the final namespace.
2. **Visibility** — public vs. private at launch.
3. **Optional tier hosting** — same repository (`data/optional/`) vs. a dedicated
   `…-attempts` repository.
4. **Data license field** — `other` + `wca-export-terms` vs. an approved SPDX value.
5. **Archive distribution** — whether to attach `wca-bench-*.tar.gz` as a Hub release
   artifact or keep archives only as local build outputs.
