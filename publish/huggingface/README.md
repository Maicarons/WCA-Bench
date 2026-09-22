---
license: other
license_name: wca-export-terms
license_link: https://www.worldcubeassociation.org/export/results
language:
- en
pretty_name: "WCA-Bench: A Sports Analytics Benchmark from World Cube Association Competition Data"
size_categories:
- 1M<n<10M
task_categories:
- tabular-regression
- tabular-classification
- time-series-forecasting
task_ids:
- tabular-single-column-regression
- tabular-multi-class-classification
annotations_creators:
- no-annotation
source_datasets:
- extended|wca
configs:
- config_name: results
  data_files:
  - split: train
    path: data/processed/results.parquet
- config_name: persons
  data_files:
  - split: train
    path: data/processed/persons.parquet
- config_name: competitions
  data_files:
  - split: train
    path: data/processed/competitions.parquet
- config_name: person_event_stats
  data_files:
  - split: train
    path: data/processed/person_event_stats.parquet
- config_name: events
  data_files:
  - split: train
    path: data/processed/events.parquet
- config_name: formats
  data_files:
  - split: train
    path: data/processed/formats.parquet
- config_name: round_types
  data_files:
  - split: train
    path: data/processed/round_types.parquet
- config_name: countries
  data_files:
  - split: train
    path: data/processed/countries.parquet
- config_name: continents
  data_files:
  - split: train
    path: data/processed/continents.parquet
- config_name: championships
  data_files:
  - split: train
    path: data/processed/championships.parquet
- config_name: split_ids
  data_files:
  - split: train
    path: data/splits/train_ids.parquet
  - split: validation
    path: data/splits/val_ids.parquet
  - split: test
    path: data/splits/test_ids.parquet
- config_name: person_history
  data_files:
  - split: train
    path: data/splits/person_history.parquet
- config_name: attempts
  data_files:
  - split: train
    path: data/optional/result_attempts.parquet
- config_name: scrambles
  data_files:
  - split: train
    path: data/optional/scrambles.parquet
tags:
- benchmark
- sports-analytics
- speedcubing
- wca
- tabular
- time-series
- causal-inference
- machine-learning
- leakage-free-evaluation
---

# Dataset Card for WCA-Bench

## Dataset Summary

**WCA-Bench** is the first comprehensive machine-learning benchmark built on the
public [World Cube Association (WCA)](https://www.worldcubeassociation.org/) competition
results database. It turns the official WCA results export (v2.0.2, ~6.9M result records
spanning 2003–2026) into a set of decoded, leakage-free tabular artifacts for sports
analytics research.

The release ships:

- **Decoded relational Parquet tables** (`persons`, `competitions`, `results`,
  `person_event_stats`, `events`, `formats`, `round_types`, `countries`, `continents`,
  `championships`) produced from the official WCA TSV export.
- **Temporal split indices** (`train` 2003–2022, `val` 2023–2024, `test` 2025–2026,
  with `Test-A`/`Test-B`/`Test-C` sub-slices).
- **Frozen training-time statistics** (`frozen_stats.json`, `person_event_stats.parquet`)
  that must be reused verbatim during evaluation to prevent temporal leakage.
- **Optional large tables** (`result_attempts`, `scrambles`) for research that needs
  per-attempt values or scramble strings.

WCA-Bench provides a single, shared evaluation protocol so that models are compared under
the same splits, the same frozen statistics, and the same stratified reporting.

- **Curated by:** WCA-Bench Project
- **Language(s):** English (metadata and documentation)
- **License:** Code — Apache-2.0; **Data — owned by the World Cube Association**, used
  under the WCA public export terms (see [License and WCA Attribution](#license-and-wca-attribution)).
- **Repository:** <https://github.com/Maicarons/WCA-Bench>

## Supported Tasks

WCA-Bench defines five core tasks computed over the same temporal splits. Each task is a
self-contained config plus a shared split protocol. The primary metric is reported on the
fixed test window (2025–2026) unless stated otherwise.

| ID | Task | Learning paradigm | Primary metric | Relevant configs |
|----|------|-------------------|----------------|------------------|
| **T1** | Result prediction | Regression | MAE / RMSE (log-scaled) | `results`, `person_history`, `person_event_stats` |
| **T2** | Placement prediction | Ranking | Kendall's τ, top-3 overlap, Brier | `results`, `person_event_stats` |
| **T3** | DNF prediction | Binary classification (imbalanced) | AUC-PR, MCC, calibration | `results`, `person_history` |
| **T4** | Human-limit estimation | Extreme-value / extrapolation | Leave-one-out stability + domain consistency | `events`, `results` |
| **T5** | Skill-transfer analysis | Causal inference | Point-estimate stability, identified-pairs count | `person_history`, `person_event_stats` |

Baseline reference results (small sampling mode, provided for sanity checking only) are
included in the `examples/` directory of the repository bundle. The values below are from the
reference run executed on an **NVIDIA GeForce RTX 4060 Laptop GPU** (`--device cuda`, PyTorch
2.13.0+cu130); the LSTM and GNN baselines train on CUDA, the boosting baselines run on GPU, and
the remaining tabular baselines run on CPU.

| Task | Best baseline (sampled, seed 42) | Primary metric | Value |
|------|----------------------------------|----------------|-------|
| T1 | `xgboost_log` | MAE (log) ↓ | 0.1639 |
| T2 | `psych_sheet` / `plackett_luce` / `kde_simulation` | Kendall's τ ↑ | 0.7673 |
| T3 | `xgboost_dnf` | AUC-PR ↑ | 0.3731 |
| T4 | `gp_evt` | leave-one-out stability ↓ | 0.9836 |
| T5 | `spearman_correlation` | identified event pairs | 413 |

Multi-seed means (seeds 42/43/44, ± standard deviation) are reported in
`examples/multi_seed.md`; full per-baseline reports are in `examples/*__*.json`.

## Dataset Structure

### Data Instances

Each config is a standalone Parquet table. There is no natural single "example row" for the
whole benchmark, so here is one representative `results` record (values abbreviated):

```json
{
  "id": 12345678,
  "pos": 1,
  "best": 415,
  "average": 539,
  "competition_id": "SomeComp2025",
  "round_type_id": "c",
  "event_id": "333",
  "person_name": "Example Cuber",
  "person_id": "2010EXAM01",
  "format_id": "a",
  "regional_single_record": "",
  "regional_average_record": "",
  "person_country_id": "USA",
  "country_id": "USA",
  "start_date": "2025-03-15",
  "date": "2025-03-15",
  "split": "test",
  "time_slice": "test_a"
}
```

### Data Fields

The tables mirror the official WCA export with a small number of derived columns added by
the WCA-Bench preprocessing pipeline.

#### `results` (~6.9M rows)

| Column | Type | Description |
|--------|------|-------------|
| `id` | int64 | Key linking to `result_attempts.result_id`. |
| `pos` | int64 | Final rank within the round (T2 supervision signal). |
| `best` | int64 | Best single of the round, encoded per `format_id` (see below). |
| `average` | int64 | Round average, present only for ao5/mo3-style formats. |
| `competition_id` | string | Foreign key into `competitions.id`. |
| `round_type_id` | string | Round type (final, semi-final, first round, …). |
| `event_id` | string | Foreign key into `events.id` (e.g. `333`, `333mbf`). |
| `person_name` | string | Contestant name as recorded at the competition. |
| `person_id` | string | WCA ID of the contestant (join key into `persons.id`). |
| `format_id` | string | Scoring format governing how `best`/`average` decode. |
| `regional_single_record` | string | Regional single-record marker (may be empty). |
| `regional_average_record` | string | Regional average-record marker (may be empty). |
| `person_country_id` | string | Country the contestant represented. |
| `country_id` | string | Country where the competition took place. |
| `start_date` | date32 | Competition start date. |
| `date` | date32 | Result date used by the temporal split. |
| `split` | string | `train` / `val` / `test` assignment. |
| `time_slice` | string | `test_a` / `test_b` / `test_c` for test rows, else empty. |

#### `persons` (~298k rows)

| Column | Type | Description |
|--------|------|-------------|
| `name` | string | Display name. |
| `gender` | string | Self-reported gender (`m` / `f` / other). |
| `wca_id` | string | WCA ID (stable identifier). |
| `sub_id` | int64 | Registration sub-id. |
| `country_id` | string | Country of representation. |
| `id` | string | Primary key (`= wca_id`, join target of `results.person_id`). |
| `continent_id` | string | Derived continent id (`_Europe`, `_Asia`, …). |
| `iso2` | string | ISO-3166 alpha-2 country code. |
| `name_country` | string | Name with country suffix, if any. |

#### `competitions` (~18.7k rows)

| Column | Type | Description |
|--------|------|-------------|
| `id` | string | Primary key (join target of `results.competition_id`). |
| `name` | string | Competition name. |
| `information` | string | Free-text description. |
| `external_website` | string | External site URL. |
| `venue` | string | Venue name. |
| `city_name` | string | City. |
| `country_id` | string | Host country id. |
| `venue_address` | string | Street address. |
| `venue_details` | string | Extra venue details. |
| `cell_name` | string | Display cell name. |
| `cancelled` | int64 | 1 if the competition was cancelled. |
| `event_specs` | string | Serialized per-event round/limit specification. |
| `delegates` | string | WCA delegates. |
| `organizers` | string | Organizers. |
| `year` / `month` / `day` | int64 | Start date components. |
| `end_year` / `end_month` / `end_day` | int64 | End date components. |
| `latitude_microdegrees` / `longitude_microdegrees` | int64 | Coordinates × 1e6. |
| `start_date` | date32 | Derived start date. |

#### `person_event_stats` (~612k rows, frozen at 2022-12-31)

| Column | Type | Description |
|--------|------|-------------|
| `person_id` | string | WCA ID. |
| `event_id` | string | Event id. |
| `mean_best` | float64 | Historical mean of `best` (training window only). |
| `std_best` | float64 | Historical std. dev. of `best`. |
| `n_attempts` | float64 | Number of recorded results. |
| `best` | float64 | Historical personal best. |
| `dnf_rate` | float64 | Historical DNF rate. |

#### `events` (22 rows), `formats` (7 rows), `round_types` (11 rows), `countries` (207 rows), `continents` (7 rows), `championships` (938 rows)

Small reference tables. `events.id` is the join key used throughout `results`; `events.format`
is one of `time`, `number`, `multi`. `formats` exposes `expected_solve_count`,
`sort_by`, `sort_by_second`, `trim_fastest_n`, `trim_slowest_n` — the last two encode the
ao5 trimming rule (see *Data Creation*). `round_types.final` flags final rounds.

#### `data/splits/*`

| File | Columns | Description |
|------|---------|-------------|
| `train_ids.parquet` | `id` | `results.id` values in the training window (2003–2022). |
| `val_ids.parquet` | `id` | Validation window (2023–2024). |
| `test_ids.parquet` | `id` | Test window (2025–2026). |
| `person_history.parquet` | `person_id`, `event_id`, `competition_id`, `date`, `best`, `average`, `split`, `time_slice` | Per-contestant chronological result history. |
| `person_event_stats.parquet` | same as `person_event_stats` | Frozen copy used by every baseline. |
| `test_time_slices.json` | — | Boundaries for `train`/`val`/`test`/`test_a`/`test_b`/`test_c`. |
| `frozen_stats.json` | — | World records, skill thresholds, continent map, global DNF rate. |

#### Optional large tables (not in the default config set)

| File | Columns | Note |
|------|---------|------|
| `data/optional/result_attempts.parquet` | `value`, `attempt_number`, `result_id` | ~137 MB, ~31.8M rows; per-attempt values. |
| `data/optional/scrambles.parquet` | `scramble`, `id`, `competition_id`, `event_id`, `group_id`, `is_extra`, `round_type_id`, `scramble_num` | ~140 MB, ~3.2M rows; scramble strings. |

### Data Splits

WCA-Bench uses **temporal** splits (never random) because neighbouring results from the
same contestant are highly correlated; a random split would leak the future into the past.

| Split | Time window | `results` rows | Purpose |
|-------|-------------|----------------|---------|
| `train` | 2003-01-01 → 2022-12-31 | 3,211,294 | Model fitting and frozen-statistic estimation. |
| `validation` | 2023-01-01 → 2024-12-31 | 1,978,851 | Hyper-parameter tuning / model selection. |
| `test` | 2025-01-01 → 2026-12-31 | 1,719,290 | Final fixed evaluation window. |

The test window is further split into three time slices for robustness reporting:

| Sub-slice | Window |
|-----------|--------|
| `test_a` | 2025-01-01 → 2025-06-30 |
| `test_b` | 2025-07-01 → 2025-12-31 |
| `test_c` | 2026-01-01 → 2026-06-30 |

Reconciliation: 6,909,435 of 6,909,454 results are assigned to a split; the 19
out-of-window rows are reported in `manifest.json` / `reconciliation.json`
(`balance_ok: true`).

## Dataset Creation

### Source Data

- **Provider:** World Cube Association, [Results Database Export](https://www.worldcubeassociation.org/export/results).
- **Snapshot format:** v2.0.2 (snake_case; `result_attempts` without `id`/`created_at`/`updated_at`).
- **Export metadata:** <https://www.worldcubeassociation.org/api/v0/export/public>.
- **Coverage:** ~298,551 contestants, ~18,708 competitions, ~6.9M results, 2003–2026.

The raw export is downloaded as TSV, decoded, and re-materialised as Parquet by the
WCA-Bench preprocessing pipeline (`scripts/download_data.py` → `scripts/build_dataset.py`).
The exact command is in the repository README.

### Encoding and Decoding Rules

Result values are **not** plain seconds. Positive values must be decoded using the
`formats` table of the corresponding event:

| `events.format` | Meaning of a positive `best`/`average` | Example |
|-----------------|----------------------------------------|---------|
| `time` | Hundredths of a second | `8653` → 1:26.53 |
| `number` | Raw count (fewest-moves only) | `28` → 28 moves |
| `multi` | Multi-blind composite encoding | see below |

Special (non-positive) values:

| Value | Meaning | Handling |
|-------|---------|----------|
| `-1` | **DNF** — Did Not Finish | Counts toward DNF rate; excluded from averages. |
| `-2` | **DNS** — Did Not Start | Usually dropped from training. |
| `0` | No result recorded | Treated as missing. |

**Multi-blind decoding.** The `333mbf` / `333mbo` events encode solved/attempted/time in a
single integer. Two formats exist and are distinguished by the first digit:

```text
Legacy format:  1 S S A A T T T T T
Modern format:  0 D D T T T T T M M
```

```python
def decode_multi(value: int) -> tuple[int, int, int]:
    """Decode a multi-blind value into (solved, attempted, seconds)."""
    s = str(value).zfill(10)
    if s[0] == "1":                     # legacy 1SSAATTTTT
        dd = 99 - int(s[1:3])
        mm = int(s[3:5])
        solved = dd + mm
        attempted = solved + mm
        seconds = int(s[5:10])
    else:                               # modern 0DDTTTTTMM
        dd = int(s[1:3])
        seconds = int(s[3:8])
        mm = int(s[8:10])
        solved = 99 - dd - mm
        attempted = solved + mm
    return solved, attempted, seconds
```

**Scramble handling for multi-blind.** A `333mbf` scramble is a sequence of several 3x3
scrambles separated by newlines; in the TSV export the newlines are replaced by `|`. Split
on `|` to recover the per-cube scramble list.

**Average-of-5 trimming (`ao5`).** Under `format_id = a` the round average discards the
fastest and slowest of five attempts and averages the remaining three. The trimming
parameters are explicit in `formats` (`trim_fastest_n`, `trim_slowest_n`). Per-attempt
values are only available in the optional `result_attempts` table. Note the rule effect: a
single DNF is usually trimmed away, but two DNFs cause the whole round to be DNF — models
should model this rule explicitly rather than averaging raw attempts.

### Splits and Leakage Prevention

- Splits are assigned by result date; competitions crossing a year boundary are grouped by
  their start date.
- `frozen_stats.json` and `person_event_stats.parquet` are computed **only** from the
  training window (frozen at 2022-12-31) and must be used **unchanged** at evaluation time.
- Any feature function must accept an explicit `as_of` timestamp so that only data strictly
  before the target competition can be used.
- Contestants whose first competition falls in the test window are flagged as cold-start
  and reported separately.

### Annotations

No human annotation was performed. All labels (result values, ranks, DNF outcomes) are
derived directly from official WCA records.

### Personal and Sensitive Information

The release contains **competition result data that is already public** on the WCA website.
It includes contestant identifiers (`person_id` / WCA ID), names as recorded at
competitions, self-reported gender, and country of representation. It does **not** contain
contact details, precise addresses, or any non-public information.

Contestants may request removal of their individual-level derived features while aggregate
statistics are retained; such requests are handled by the project maintainers as described
in the project data card.

## Considerations for Using the Data

**Social impact and bias.**

- **Event imbalance.** Data volume is highly skewed: 3x3x3 dominates, while blindfolded and
  multi-blind events are comparatively rare. Aggregate metrics are therefore dominated by
  the 3x3x3 event; always report per-event stratified results.
- **Geographic imbalance.** Participation opportunities are not evenly distributed across
  countries and continents, which limits claims about cross-region generalisation.
- **Class imbalance for DNF.** DNF rates differ sharply between events, so classification
  metrics such as AUC-PR must be interpreted per event.
- **Non-stationarity.** Rules, hardware, and community practice changed over 2003–2026, so
  the result distribution is not stationary; a model that fits early data may not transfer
  to the test window.
- **Self-selection in transfer analysis.** Contestants choose which events to enter, so
  naive correlations overstate causal skill-transfer effects (T5 addresses this).
- **Representation of gender.** Gender is self-reported and may be missing or inconsistent
  in older records; avoid using it for individual-level profiling.

**Discussion of risks and harms.** The most salient risk is misuse for gambling/betting or
for discriminatory profiling of individual contestants. These uses are explicitly
prohibited (see below) and are incompatible with the WCA's public-data terms.

## License and WCA Attribution

- **Code** (the WCA-Bench repository, preprocessing pipeline, and baselines) is released
  under the **Apache License 2.0**.
- **Data** is owned by the **World Cube Association** and is redistributed here under the
  WCA public export terms. Whenever information based on the WCA export is republished,
  the following attribution must be included verbatim:

> This information is based on competition results owned and maintained by the
> World Cube Association, published at https://worldcubeassociation.org/results

See the WCA export documentation for the authoritative terms:
<https://www.worldcubeassociation.org/export/results>.

## Prohibited Uses

The following uses violate this dataset's terms and the WCA-Bench data card:

- **Gambling, betting, or any form of wagering prediction.** The data must not be used to
  predict or facilitate bets on competition outcomes.
- **Discriminatory screening, profiling, or shaming of individual contestants.** Do not use
  individual-level data to rank, target, or harass people.
- **Impersonating official bodies or forging competition results.** Do not present
  derivative output as if it originated from the WCA or any competition organiser.
- **Redistribution of individual-level, privacy-sensitive derived data without
  anonymisation.**

## Citation

If you use WCA-Bench, please cite it:

```bibtex
@misc{wcabench2026,
  title        = {WCA-Bench: A Sports Analytics Benchmark from World Cube Association Competition Data},
  author       = {{WCA-Bench Project}},
  year         = {2026},
  version      = {0.1.0},
  howpublished = {\url{https://github.com/Maicarons/WCA-Bench}},
  note         = {Data based on competition results owned and maintained by the World Cube Association}
}
```

## Getting Started

```bash
# 1. Install the benchmark package
pip install -e ".[dev,fast,boost]"

# 2. Load a table with the Datasets library
python - <<'PY'
from datasets import load_dataset
ds = load_dataset("Maicarons/WCA-Bench", "results", split="train")
print(ds)
PY

# 3. Reproduce the baselines (see the repository README for the full pipeline)
python scripts/run_all_baselines.py --mode small
python scripts/build_leaderboard.py
```

A machine-readable description of the release layout is in `publish/DATASET_LAYOUT.md` in
the source repository.
