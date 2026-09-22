# Phase 1: Data Infrastructure (Months 1–3)

> **Objective**: Build a reproducible, high-performance data infrastructure that parses the domain rules correctly.
> **Exit milestone**: [M1 Data Pipeline Complete](/plan/roadmap#m1-·-data-pipeline-complete-month-3)

## 1. Phase Objectives

- Download and parse the official WCA database export
- Implement the data preprocessing pipeline (result decoding, temporal splitting, feature engineering)
- Build the data loader and caching system
- Write the Data Card and documentation

## 2. Work Breakdown (WBS)

| Task ID | Task name | Weeks | Prerequisites | Deliverables | Role |
| --- | --- | --- | --- | --- | --- |
| P1-T1 | Environment and repository scaffolding | W1 | — | `pyproject.toml`, directory structure, CI skeleton | Engineer |
| P1-T2 | Data acquisition and raw validation | W1–W2 | P1-T1 | `scripts/download_data.sh`, validation report | Data engineer |
| P1-T3 | Result value decoding module | W2–W3 | P1-T2 | `data/decoders.py` (time/number/multi) | Data engineer |
| P1-T4 | Scramble sequence normalization | W3 | P1-T2 | `333mbf` multi-line restoration logic | Data engineer |
| P1-T5 | Round format normalization | W3–W4 | P1-T3 | average reconstruction + consistency checks | Data engineer |
| P1-T6 | Feature engineering | W4–W6 | P1-T5 | `data/features.py` (competitor/event/head-to-head/time) | ML engineer |
| P1-T7 | Temporal splitting and frozen statistics | W6–W7 | P1-T6 | `data/splits.py`, `data/splits/*` | Data engineer |
| P1-T8 | Parquet export and performance optimization | W7–W8 | P1-T7 | Columnar artifacts, performance benchmark report | Data engineer |
| P1-T9 | Data loader and streaming support | W8–W9 | P1-T8 | `data/loader.py`, caching system | ML engineer |
| P1-T10 | Data card and documentation | W9–W10 | P1-T8 | `datacard.md`, documentation pages | Documentation maintainer |
| P1-T11 | Quality checks and testing | W10–W12 | P1-T3~T9 | Test suite, QA report | Everyone |

> Weeks are **relative weeks** (W1 = the project's 1st week); the phase lasts 12 weeks in total.

## 3. Detailed Task Descriptions

### P1-T1 · Environment and Repository Scaffolding

- Initialize `pyproject.toml` (Python version, dependency groups, tool configuration)
- Set up the `src/wca_bench/` package layout and the `tests/` structure
- Configure GitHub Actions (`ci.yml`, `lint.yml`, `docs.yml`)
- **Deliverable**: a runnable repository skeleton + green CI

### P1-T2 · Data Acquisition and Raw Validation

- Download the official WCA export (recording the snapshot version, e.g. v2.0.2)
- Validate table existence, headers, encoding, and row counts
- Produce a validation report (row counts, fields, and anomaly counts per table)
- **Deliverables**: `scripts/download_data.sh`, `reports/data_ingest.md`

### P1-T3 · Result Value Decoding Module

- Implement decoding for `time` (hundredths of a second), `number` (move count), and `multi` (multi-blind)
- Handle special values: `-1` DNF, `-2` DNS, `0` no result
- Bi-directional reversibility tests for multi-blind (`encode(decode(v)) == v`)
- **Deliverables**: `data/decoders.py` + unit tests

### P1-T4 · Scramble Sequence Normalization

- `333mbf` scrambles: split on `|` and restore the multiple lines
- Normalize whitespace and escaping, and validate lengths
- **Deliverables**: scramble normalization functions + coverage tests

### P1-T5 · Round Format Normalization

- Reconstruct the attempt sequence from `result_attempts`
- Compute the standardized average according to `format_id` (best of 3 / ao5 / mo3)
- Cross-check against the official `results.average` and log warnings
- **Deliverables**: round normalization module + agreement-rate report

### P1-T6 · Feature Engineering

| Feature family | Examples |
| --- | --- |
| Competitor static | Age, gender, nationality, total number of competitions |
| Sequence features | Last N attempts, rolling mean/variance, trend slope |
| Event context | Event ID, round type, format |
| Head-to-head features | Number of competitors in the round, distribution of opponents' historical strength |
| Temporal context | Days since the last competition, season, competition tier |
| DNF-related | Historical DNF rate, recent DNF count |

- **Key constraint**: all feature function signatures must accept `as_of`
- **Deliverables**: `data/features.py` + feature dictionary documentation

### P1-T7 · Temporal Splitting and Frozen Statistics

- Generate train (2003–2022) / val (2023–2024) / test (2025–2026) indices
- Generate the boundaries of the test time subsets Test-A/B/C
- Compute and freeze benchmark statistics (competitor historical means, world records, skill percentile thresholds)
- Generate per-competitor longitudinal sequences
- **Deliverables**: `data/splits/*`, `data/splits.py`

### P1-T8 · Parquet Export and Performance Optimization

- Polars loading + Parquet export
- Column pruning and predicate pushdown configuration
- Benchmarking: loading time and memory footprint (against Pandas)
- **Deliverables**: Parquet artifacts, performance report

### P1-T9 · Data Loader and Streaming Support

- A unified `Dataset` interface
- Caching of frequently accessed competitor features
- A streaming loader (for memory-constrained environments)
- **Deliverables**: `data/loader.py` + usage examples

### P1-T10 · Data Card and Documentation

- The data card covers: sources, scale, field semantics, splits, known biases, permitted/prohibited uses
- Update the documentation site pages under `docs/data/` accordingly
- **Deliverables**: `datacard.md`, documentation pages

### P1-T11 · Quality Checks and Testing

- Run the [Data Quality Checklist](/data/pipeline#_7-data-quality-checklist)
- Unit test coverage of core modules ≥ 80%
- Small-sample end-to-end tests (run in CI)
- **Deliverables**: test suite, QA report

## 4. Phase Deliverables

| ID | Deliverable | Corresponding tasks |
| --- | --- | --- |
| D2 | Preprocessing pipeline and data loader | P1-T3 ~ P1-T9 |
| D3 | Data Card | P1-T10 |
| — | Parquet data artifacts + split indices | P1-T7, P1-T8 |
| — | Test suite and QA report | P1-T11 |

## 5. Phase Acceptance Criteria

- [ ] `scripts/build_dataset.py` produces all Parquet artifacts from raw data with a single command
- [ ] Artifact checksums (SHA256) are identical across repeated runs
- [ ] Multi-blind decoding round-trip consistency is 100%
- [ ] The agreement rate between reconstructed average and the official value reaches the threshold
- [ ] Split indices reconcile exactly with raw table row counts
- [ ] No future information leakage (all `assert_no_leakage` tests pass)
- [ ] Unit test coverage of core modules ≥ 80%
- [ ] The data card is complete and has passed review

## 6. Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Edge cases in multi-blind encoding | Decoding errors contaminate all tasks | Round-trip tests + manual sampling checks |
| Export snapshot updates | Results become incomparable | Pin the snapshot version and record it in the data card |
| Insufficient memory (6.6M rows) | The pipeline cannot run | Polars + streaming loader |

## 7. Further Reading

- [Phase 2: Task Definition and Baselines →](/plan/phase-2)
- [Dependencies →](/plan/dependencies)
