# Acceptance Criteria

This chapter defines **decidable** acceptance criteria for each phase and for the final delivery.

## 1. Acceptance Principles

| Principle | Description |
| --- | --- |
| Decidable | Every criterion can be judged with yes/no or a numeric threshold |
| Reproducible | The acceptance process itself is repeatable and does not rely on subjective impressions |
| Traceable | Every criterion maps to a specific task and deliverable |
| Layered | Phase acceptance → milestone acceptance → final project acceptance |

## 2. Phase Acceptance Criteria

> **Status as of 2026-09-21.** Markers: `[x]` complete · `[~]` partial · `[ ]` not met. The evidence behind each marker is summarised in the [Conformance Audit](/plan/audit), and cited criterion by criterion in the repository's `AUDIT.md`.

### A1 Data Pipeline

**Corresponds to**: Phase 1 / M1

- [x] **Complete** — `scripts/build_dataset.py --source raw|synthetic` produces all Parquet artifacts from raw data in one command
- [~] **Partial** — `data/processed/manifest.json` records counts, but there is no checksum manifest and no reproducibility test
- [x] **Complete** — `decoders.py::decode_multi` / `encode_multi` (both `1SSAATTTTT` and `0DDTTTTTMM`), covered by `tests/unit/test_decoders.py`
- [~] **Partial** — `data/processed/reconciliation.json` holds a summary only; the rate is not asserted in a test
- [x] **Complete** — `data/splits/{train,val,test}_ids.parquet` reconciled in `reconciliation.json`
- [x] **Complete** — `splits.py::assert_no_leakage`, forwarded by `evaluation/protocol.py`; `features.py` enforces a keyword-only `as_of`
- [~] **Partial** — `pytest-cov` and `[tool.coverage.run]` are in place and CI runs `--cov=wca_bench`; a numeric ≥ 80 % threshold is not enforced yet
- [x] **Complete** — `datacard.md` (EN) + `datacard_zh.md` (ZH), including allowed and prohibited uses
- [ ] **Not met** — no benchmark script and no reported measurement

### A2 Task Definition

**Corresponds to**: Phase 2 / M2

- [x] **Complete** — `docs/tasks/*`: each page carries definition, inputs/outputs, metrics, baselines and domain challenges
- [~] **Partial** — metrics and stratification are specified; pairing units are documented centrally in `docs/evaluation/statistics` rather than on each task page
- [x] **Complete** — `configs/task3_dnf_rate.yaml` (`hard_subset.historical_dnf_rate: [0.1, 0.3]`); `evaluation/stratified.py` accepts a hard-subset mask
- [x] **Complete** — `Report.extras["cold_start"]`, present in the `examples/` reports
- [ ] **Not met** — no review record and no explicit frozen-version marker

### A3 Baseline Implementation

**Corresponds to**: Phase 2 / M3

- [x] **Complete** — 21 baselines, 4–5 per task (target was ≥ 18); see [Task Suite · Baseline Inventory](/tasks/#_5-baseline-inventory)
- [x] **Complete** — `.github/workflows/ci.yml` runs `run_all_baselines.py --mode small`; `tests/integration/test_end_to_end.py` iterates the task registry
- [x] **Complete** — every report carries `overall` + four-way stratification + `significance` + `cost`
- [x] **Complete** — `scripts/build_leaderboard.py` → `examples/leaderboard.{md,csv}`
- [x] **Complete** — 22 `configs/*.yaml` files cover all 21 baselines
- [x] **Complete** — seeds 42 / 43 / 44 aggregated by `scripts/run_multi_seed.py` into `examples/multi_seed.md`, covering all 21 baselines
- [x] **Complete** — `evaluation/significance.py` is invoked by the task runner and persisted in each report

### A4 Release

**Corresponds to**: Phase 3 / M4, M5

- [ ] **Not met** — external submission step
- [x] **Complete** — `paper/sections/08_limitations_ethics.tex`
- [x] **Complete** — `README` / `LICENSE` (Apache-2.0) / `CONTRIBUTING` / `CODE_OF_CONDUCT` / `CITATION.cff`, with Chinese counterparts; the `CITATION.cff` placeholder URL has been fixed
- [x] **Complete** — `publish/huggingface/`: dataset card, `dataset_infos.json`, LFS attributes, dry-run uploader
- [x] **Complete** — `publish/huggingface/upload_models.py` publishes the baseline reports as a model repository
- [x] **Complete** — bilingual site (`/` + `/zh/`) builds and passes the link/anchor check; deployment runs through `docs.yml`
- [x] **Complete** — `scripts/validate_submission.py`, exercised in CI against `examples/submission_template/`
- [ ] **Not met** — external
- [ ] **Not met** — external

### A5 Iteration and Expansion

**Corresponds to**: Phase 4 / M6

- [ ] **Not met** — no community feedback collected yet
- [ ] **Not met** — no v1.1 and no changelog
- [ ] **Not met** — depends on a post-window data release
- [x] **Complete** — graph (`gnn`), Bayesian (`beta_binomial`, `hierarchical_shrinkage`) and causal (`iv_2sls`, `causal_forest`) baselines added to the leaderboard
- [ ] **Not met** — external
- [ ] **Not met** — external
- [ ] **Not met** — maintainer handbook and roadmap v2 not written

## 3. Final Delivery Acceptance

| ID | Deliverable | Acceptance criterion |
| --- | --- | --- |
| D1 | WCA-Bench dataset | Loadable, complete card, covering the 17 active events |
| D2 | Preprocessing pipeline and loader | Reproducible with a single command, test coverage meets the target |
| D3 | Data card | Includes sources/scale/fields/splits/biases/usage constraints |
| D4 | Five task definitions and evaluation protocol | All five elements present, reviewed and frozen |
| D5 | Baseline implementations and results | ≥ 18 baselines, complete Report structure |
| D6 | Leaderboard and submission specification | Rebuildable with one command, submission validation usable |
| D7 | Main paper | Submitted to NeurIPS E&D |
| D8 | Public code repository | Public, CI green, complete governance files |
| D9 | Challenge and results analysis | Competition live + analysis report |

## 4. Quality Gates

Every PR / release must pass:

```text
Gate 1  Lint and type checks pass
Gate 2  All unit tests pass, coverage does not decrease
Gate 3  Small-sample end-to-end tests pass
Gate 4  The documentation site builds successfully
Gate 5  No future-information-leakage assertions fail
Gate 6  (At release) reproduction level ≥ L2; main leaderboard ≥ L3
```

## 5. Adjudication and Exemptions

| Case | Handling |
| --- | --- |
| A criterion is unattainable for external reasons | The PI records it in writing, adjusts it, and adds it to the changelog |
| A breaking change invalidates an existing criterion | Establish a new criterion through the versioning mechanism; do not retroactively change the old leaderboard |
| A metric threshold needs adjustment | Requires review by ≥ 2 people and a recorded justification |

## 6. Further Reading

- [Risks and Mitigation →](/plan/risks)
- [Milestones](/plan/roadmap#_2-key-milestones)
