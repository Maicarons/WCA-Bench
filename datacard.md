# WCA-Bench Data Card

> This data card follows the *Datasheets for Datasets* convention and is the authoritative
> statement of what the WCA-Bench dataset contains and how it may be used.

## 1. Basic information

| Field | Value |
| --- | --- |
| Name | WCA-Bench |
| Version | 0.1.0 |
| Data source | World Cube Association Results Database Export |
| Export format | v2.0.2 (snake_case, includes `result_attempts`) |
| Official description | https://www.worldcubeassociation.org/export/results |
| API metadata | https://www.worldcubeassociation.org/api/v0/export/public |
| Code licence | Apache-2.0 |
| Data rights | World Cube Association |
| Data card language | English (see `datacard_zh.md` for Simplified Chinese) |

## 2. Scale

### 2.1 Official export (approximate)

| Table | Scale |
| --- | --- |
| `persons` | ~298k |
| `competitions` | ~18.7k |
| `results` | ~6.9M |
| `result_attempts` | one row per attempt for formats that record individual attempts |
| `scrambles` | ~3.1M |
| `events` | 17 active events plus retired events |

### 2.2 WCA-Bench release artefacts

| Artefact | Description |
| --- | --- |
| `data/processed/*.parquet` | Decoded and normalized tables |
| `data/processed/person_event_stats.parquet` | Frozen per-person, per-event statistics |
| `data/processed/frozen_stats.json` | Frozen benchmark statistics computed from the training window |
| `data/splits/{train,val,test}_ids.parquet` | Row-level split indices |
| `data/splits/person_history.parquet` | Per-person, chronologically ordered participation history |
| `data/splits/test_time_slices.json` | Boundaries of Test-A / Test-B / Test-C |

A small **synthetic** export (`scripts/generate_synthetic.py`) is also provided for CI and offline
development. It is generated from a fixed seed, contains no real personal data, and must never be
reported as a benchmark result.

## 3. Field semantics

- `best` / `average`: best single and average for the round.
- Sentinel values: `-1` = DNF (did not finish), `-2` = DNS (did not start), `0` = no result.
- Positive values are interpreted according to the event `format`:
  - `time`: hundredths of a second (`8653` = 1:26.53).
  - `number`: move count (fewest moves); the stored average is 100× the mean.
  - `multi`: multi-blind composite encoding (see below).
- `333mbf` scrambles: line breaks are encoded as `|` in the TSV export and are restored during
  preprocessing.

### 3.1 Multi-blind encoding

Multi-blind results use a composite decimal encoding:

```text
legacy : 1 S S A A T T T T T     (solved / attempted / seconds)
current: 0 D D T T T T T M M     (difference / seconds / missed)
```

`wca_bench.data.decoders` implements both directions plus a round-trip invariant
(`encode(decode(v)) == v`) that is covered by unit tests.

### 3.2 Round-format normalization

- *best of 3*: minimum of the three attempts.
- *average of 5*: arithmetic mean after removing the best and the worst attempt.
- *mean of 3*: arithmetic mean of the three attempts.

Reconstructed averages are reconciled against the official `results.average` values; the
reconciliation summary is written to `data/processed/reconciliation.json`.

## 4. Splits

| Split | Window | Purpose |
| --- | --- | --- |
| train | 2003–2022 | Fitting and estimation of benchmark statistics |
| validation | 2023–2024 | Hyper-parameter tuning and model selection |
| test | 2025–2026 | Final evaluation (frozen window) |
| Test-A / B / C | 2025H1 / 2025H2 / 2026H1 | Temporal robustness slices |

The split is **temporal, not random**, and the main leaderboard is always evaluated on the fixed
2025–2026 window. Data arriving after the window is released separately as an *Extended Test Set*.

## 5. Known biases and limitations

- **Uneven event coverage.** Third-order solving dominates by volume; big-blind and multi-blind
  events have far fewer records.
- **Regional inequality.** Access to competitions differs sharply by country, which limits
  conclusions about cross-regional generalization.
- **Class imbalance.** DNF rates vary widely across events, making classification metrics sensitive
  to threshold choice.
- **Non-stationarity.** Rule changes, hardware evolution, and training-method shifts make the score
  distribution non-stationary over the 23-year history.
- **Self-selection in skill transfer.** Athletes choose when to start new events, so naive
  correlations systematically overstate causal transfer effects.
- **No demographic inference.** The dataset must not be used to infer personal attributes beyond
  the fields published by the WCA.

## 6. Allowed uses

- Research and teaching in sports analytics, benchmark methodology, and reproducible evaluation.
- Community service: performance analysis for athletes, and round/advancement design support for
  competition organizers.
- Aggregate statistical analysis and method comparison.

## 7. Prohibited uses

- Gambling, betting, or any form of wager prediction.
- Discriminatory screening, profiling, or harassment of individual athletes.
- Impersonating official bodies or falsifying competition results.
- Redistributing individual-level, privacy-sensitive derived data without anonymization.

## 8. Attribution requirement

Any redistribution of information derived from the WCA export must include:

> This information is based on competition results owned and maintained by the
> World Cube Association, published at https://worldcubeassociation.org/results

## 9. Ethics and opt-out

- Athletes may contact the maintainers to request removal of their records from individual-level
  derived features. Aggregate statistics are retained.
- The project commits to complying with the WCA public-data usage terms.
- The benchmark is published as a research artefact; it is not a ranking authority and must not be
  presented as one.

## 10. Reproduction entry point

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev,fast,boost]"
python scripts/generate_synthetic.py --small
python scripts/build_dataset.py --source synthetic
python scripts/run_all_baselines.py --mode small
python scripts/build_leaderboard.py
```

Real data: run `python scripts/download_data.py` followed by
`python scripts/build_dataset.py --source raw`.
