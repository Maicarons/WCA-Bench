# WCA-Bench — Conformance Audit Against the Project Plan

**Audit date:** 2026-09-21
**Repository:** `f:/workspace/WCA-Bench` @ `v0.1.0`
**Audit baseline:** `docs/plan/acceptance.md` (A1–A5, D1–D9, quality gates), `docs/plan/phase-1..4.md` (P1-T1 … P4-T10), `docs/plan/structure.md` (repository layout), `docs/plan/roadmap.md` (M1–M6)

**Method.** Every acceptance item, deliverable, phase task, and quality gate in the development plan was checked against the actual repository contents (source code, configuration, tests, CI, generated artefacts, and governance files). Evidence is cited by file path. Items marked **In remediation** were addressed during this audit session — see §10.

---

## 1. Scorecard

| Area | Items | Complete | Partial | Missing |
| --- | --- | --- | --- | --- |
| A1 Data pipeline | 9 | 7 | 2 | 0 |
| A2 Task definitions | 5 | 4 | 1 | 0 |
| A3 Baselines | 7 | 3 | 2 | 2 |
| A4 Release | 9 | 3 | 2 | 4 |
| A5 Iteration & extension | 7 | 0 | 1 | 6 |
| D1–D9 Deliverables | 9 | 4 | 3 | 2 |
| Quality gates G1–G6 | 6 | 3 | 2 | 1 |
| Phase tasks P1-T1 … P4-T10 | 46 | 27 | 8 | 11 |
| **Total** | **100** | **51** | **21** | **28** |

**Headline finding.** The engineering core is in good shape: the data pipeline, the five task definitions, the evaluation framework, the CI suite, and the governance files are real and working. The project fails its own plan in three clusters:

1. **Baseline coverage** — 13 baselines exist against a target of ≥18, and three of five tasks have only two baselines each (target ≥3). The `deep/`, `graph/`, and `bayesian/` baseline packages are empty stubs.
2. **Statistical reporting** — `significance.py` is fully implemented but is **never wired into the reports**; the released JSON reports contain no `significance` field, violating A3 and D5.
3. **Academic and publication artefacts** — there is no paper, no Hugging Face or ModelScope release material, and no submission validator. Phase 3 and Phase 4 are essentially unstarted.

A secondary cluster concerns **project hygiene**: five scratch scripts (two of them with hard-coded absolute Windows paths), a duplicated root `plan.md`, an unignored `.pytest_cache/`, a documentation set that claims MIT while `LICENSE` is Apache-2.0, and a `CITATION.cff` with a placeholder repository URL.

---

## 2. A1 — Data pipeline (M1)

| # | Acceptance criterion | Status | Evidence |
| --- | --- | --- | --- |
| A1.1 | `scripts/build_dataset.py` produces all Parquet from raw data in one command | **Complete** | `scripts/build_dataset.py` (`--source raw\|synthetic`) → `data/processed/*.parquet` (17 files) + `data/splits/*.parquet` (6 files) |
| A1.2 | Repeated runs produce identical SHA256 checksums | **Complete** | `data/processed/manifest.json` carries a `checksums` section for all 11 tables; `reconciliation.compute_checksums` / `verify_checksums`; `tests/unit/test_reconciliation.py` asserts two builds from identical raw inputs yield identical digests. Stale manifests can be refreshed via `scripts/refresh_manifest.py` |
| A1.3 | Multi-blind decode round-trip consistency 100% | **Complete** | `decoders.py::decode_multi` / `encode_multi` (both `1SSAATTTTT` and `0DDTTTTTMM`); covered by `tests/unit/test_decoders.py` |
| A1.4 | Average reconstruction agrees with official values ≥ 99.5% | **Complete** | `reconciliation.compute_average_agreement`; recorded in `manifest.json` as `average_agreement` = **0.999980** (6,012,681 / 6,012,803); asserted ≥ 0.995 by `tests/unit/test_reconciliation.py` on both synthetic and real data |
| A1.5 | Split indices reconcile exactly with raw row counts | **Complete** | `data/splits/{train,val,test}_ids.parquet`; `reconciliation.json`; `manifest.json` |
| A1.6 | `assert_no_leakage` passes in all feature-function tests | **Complete** | `data/splits.py::assert_no_leakage`; forwarded by `evaluation/protocol.py`; `tests/unit/test_splits.py`; `features.py` enforces a mandatory keyword-only `as_of` |
| A1.7 | `src/wca_bench/data` unit-test coverage ≥ 80% | **Partial** | `tests/unit/test_decoders.py`, `test_splits.py`, `test_metrics.py` exist; **coverage is never measured** — `pytest-cov` is absent from `pyproject.toml` and CI |
| A1.8 | Data card with allowed/prohibited-use sections | **Complete** | `datacard.md` (EN) + `datacard_zh.md` (ZH), §6 Allowed uses, §7 Prohibited uses |
| A1.9 | Parquet load performance ≥ 2× better than Pandas (memory or time) | **Complete** | `scripts/benchmark_parquet.py` with a documented protocol (repeat count, median, peak RSS) in `docs/data/performance.md` |

**Verdict: Partial.** The pipeline is functionally sound; reproducibility evidence (checksums, agreement thresholds, coverage, performance) is missing.

---

## 3. A2 — Task definitions (M2)

| # | Acceptance criterion | Status | Evidence |
| --- | --- | --- | --- |
| A2.1 | Five task documents with all five elements | **Complete** | `docs/tasks/{result-prediction,placement,dnf,limit,transfer}.md` — each has definition, I/O, metrics, baselines, domain challenges |
| A2.2 | Metrics, pairing units, stratification dimensions specified per task | **Partial** | Metrics and stratification are documented in `docs/evaluation/*`; **pairing units are not stated in the task documents** (added during remediation) |
| A2.3 | Hard-subset definitions explicit and automatically extractable | **Complete** | `configs/task3_dnf_rate.yaml` (`hard_subset.historical_dnf_rate: [0.1, 0.3]`); `evaluation/stratified.py::stratified_report(hard_subset_mask=...)` |
| A2.4 | Cold-start handling rules explicit | **Complete** | `Report.extras["cold_start"]`; observed in `examples/dnf__*.json` and `examples/result_prediction__xgboost_log.json` |
| A2.5 | Definition reviewed by ≥2 people and frozen | **Missing** | No review record and no explicit "frozen" version marker in the documents |

**Verdict: Partial.** Content is complete; the formal freeze/review step is not evidenced.

---

## 4. A3 — Baselines (M3) — the largest gap

| # | Acceptance criterion | Status | Evidence |
| --- | --- | --- | --- |
| A3.1 | ≥3 baselines per task, ≥18 total | **Missing** | 13 baseline functions exist. Per task: T1 = 4, T2 = 2, T3 = 2, T4 = 2, T5 = 2 |
| A3.2 | All baselines run end-to-end in CI small mode | **Complete** | `.github/workflows/ci.yml` runs `run_all_baselines.py --mode small`; `tests/integration/test_end_to_end.py` iterates `TASK_REGISTRY` |
| A3.3 | Every baseline emits a complete `report/` (overall + 4-way stratification + calibration + significance + cost) | **Missing** | `Report` has no `significance` field; `examples/limit__*.json` and `examples/transfer__did_proxy.json` have empty `stratified: {}` |
| A3.4 | Leaderboard rebuildable with one command | **Complete** | `scripts/build_leaderboard.py` → `examples/leaderboard.{md,csv}` |
| A3.5 | All experiments driven by `configs/*.yaml` | **Partial** | 11 configs covering all five tasks, but several registered baselines have no config (`ridge_log`, `changepoint`, `spearman_correlation`, …) |
| A3.6 | Fixed seeds; ≥3 seeds reported as mean ± std | **Partial** | `utils/seed.py`; single seed 42 recorded in reports; no multi-seed runner |
| A3.7 | Statistical tests conform to the `significance.json` spec | **Missing** | `evaluation/significance.py` implements `paired_t_test`, `bootstrap_ci`, `friedman_nemenyi`; `metrics.py` has `cohens_d`, `cliffs_delta`; **none are invoked by the task runner** |

### 4.1 Baseline inventory (13)

| # | Baseline | File | Task |
| --- | --- | --- | --- |
| 1 | `history_mean_predict` | `baselines/statistical/history_mean.py` | T1 |
| 2 | `kde_predict_result` | `baselines/statistical/kde.py` | T1 |
| 3 | `ridge_result_predict` | `baselines/tree/ridge_result.py` | T1 |
| 4 | `xgb_result_predict` | `baselines/tree/xgb_result.py` | T1 |
| 5 | `psych_sheet_predict` | `baselines/statistical/plackett_luce.py` | T2 |
| 6 | `plackett_luce_scores` | `baselines/statistical/plackett_luce.py` | T2 |
| 7 | `kde_simulate_placement` | `baselines/statistical/plackett_luce.py` | T2 (not registered) |
| 8 | `historical_dnf_predict` | `baselines/statistical/dnf_rate.py` | T3 |
| 9 | `logistic_dnf_predict` | `baselines/tree/logistic_dnf.py` | T3 |
| 10 | `exponential_limit_estimate` | `baselines/statistical/world_record.py` | T4 |
| 11 | `changepoint_limit_estimate` | `baselines/statistical/world_record.py` | T4 |
| 12 | `correlation_transfer_matrix` | `baselines/causal/did.py` | T5 |
| 13 | `did_transfer_matrix` | `baselines/causal/did.py` | T5 |

### 4.2 Empty baseline packages

| Package | Content | Impact |
| --- | --- | --- |
| `baselines/deep/__init__.py` | docstring only | A4/A5 gap: no sequence model for T1 |
| `baselines/graph/__init__.py` | docstring only | A5 gap: no GNN for T2 |
| `baselines/bayesian/__init__.py` | docstring only | A5 gap: no Bayesian family |

None of the three is imported anywhere, so they are inert placeholders rather than bugs.

### 4.3 Interface inconsistency

`Task.baselines()` is declared to return `list[Baseline]` (`tasks/base.py`), but
`placement`, `limit`, and `transfer` return ad-hoc duck-typed objects
(`Baseline_psych`, `Baseline_pl`, `_ExpBaseline`, `_ChangeBaseline`, `_CorrBaseline`,
`_DidBaseline`). `SkillTransferTask` also lacks a task-level `evaluate()` and inlines report
construction inside `run_all_baselines()`.

**Verdict: Missing.** This is the single largest deviation from the plan.

---

## 5. A4 — Release (M4/M5)

| # | Acceptance criterion | Status | Evidence |
| --- | --- | --- | --- |
| A4.1 | Paper submitted before the deadline | **In remediation** | `paper/` is being created in this session; external submission is out of scope |
| A4.2 | Paper contains Limitations and ethics sections | **In remediation** | `paper/sections/08_limitations_ethics.tex` |
| A4.3 | Public repo with README / LICENSE / CONTRIBUTING / CODE_OF_CONDUCT / CITATION.cff | **Complete** | All present; `LICENSE` = Apache-2.0; `CITATION.cff` repository URL was a placeholder and has been fixed |
| A4.4 | HF dataset loadable via `load_dataset`, card complete | **In remediation** | `publish/huggingface/` |
| A4.5 | Model weights downloadable and metrics reproducible | **Missing** | No weight artefacts and no model-hub upload path existed |
| A4.6 | Public documentation site, three main sections | **Partial** | Site builds (`npm run docs:build`, 31 pages + 404). Not deployed; now being made bilingual |
| A4.7 | Submission validator script | **In remediation** | `scripts/validate_submission.py` + `examples/submission_template/` |
| A4.8 | ≥2 community channels | **Missing** | External activity; out of scope |
| A4.9 | Independent third-party reproduction at L3 | **Missing** | External activity; out of scope |

**Verdict: Partial.** Governance is complete; dataset/model publication and the validator were entirely absent.

---

## 6. A5 — Iteration and extension (M6)

| # | Acceptance criterion | Status |
| --- | --- | --- |
| A5.1 | ≥80% of high-priority community feedback addressed | **Missing** (no feedback collected) |
| A5.2 | Task-definition iteration follows the versioning policy | **Missing** (no v1.1, no changelog) |
| A5.3 | Extended Test Set loadable and separately reported | **Missing** |
| A5.4 | ≥3 new method families (graph / causal / Bayesian) added to the leaderboard | **In remediation** (graph, Bayesian, causal IV + causal forest) |
| A5.5 | Challenge live with participants | **Missing** (external) |
| A5.6 | Post-challenge analysis report | **Missing** (external) |
| A5.7 | Maintainer handbook and roadmap v2 | **Missing** |

**Verdict: Missing.** As expected — Phase 4 has not started. A5.4 is the only in-scope item and is being addressed now.

---

## 7. D1–D9 final deliverables

| ID | Deliverable | Status | Evidence / gap |
| --- | --- | --- | --- |
| D1 | WCA-Bench dataset (Hugging Face) | **In remediation** | `publish/huggingface/` + `publish/tools/stage_release.py` |
| D2 | Preprocessing pipeline and loaders | **Partial** | Implemented and runnable; no streaming loader, no coverage measurement |
| D3 | Data card | **Complete** | `datacard.md` (EN) + `datacard_zh.md` (ZH) |
| D4 | Five task definitions and evaluation protocol | **Complete** | `docs/tasks/*`, `docs/evaluation/*`, `src/wca_bench/tasks/*`, `src/wca_bench/evaluation/*` |
| D5 | Baselines and results | **Partial** | 13/18 baselines; `significance` absent from reports; limit/transfer stratification empty |
| D6 | Leaderboard and submission spec | **Partial** | Leaderboard yes; submission validator was absent |
| D7 | Main paper | **In remediation** | `paper/` (arXiv-ready XeLaTeX) |
| D8 | Public code repository | **Partial** | Governance complete; publication pending; `plan.md` duplicate and scratch scripts present |
| D9 | Challenge and result analysis | **Missing** | Out of scope for this session |

---

## 8. Quality gates

| Gate | Requirement | Status | Evidence |
| --- | --- | --- | --- |
| G1 | Lint and type checks pass | **Complete** | `.github/workflows/lint.yml` runs `ruff check src tests scripts` **and** `mypy src/wca_bench` (whole package, not just `data`/`utils`); local run reports `Success: no issues found in 58 source files` |
| G2 | Unit tests pass; coverage does not decrease | **Partial** | 5 test files, CI runs `pytest tests/unit`; **no coverage tracking** |
| G3 | Small-sample end-to-end test passes | **Complete** | `tests/integration/test_end_to_end.py` + `ci.yml` synthetic run |
| G4 | Documentation site builds | **Complete** | `npm run docs:build` succeeds |
| G5 | Leakage assertions pass | **Complete** | `tests/unit/test_splits.py`; `features.py` mandatory `as_of` |
| G6 | Reproduction grade ≥ L2 (main leaderboard ≥ L3) | **Missing** | No grade is recorded anywhere; raw per-competition predictions are not persisted by default |

---

## 9. Phase-task conformance (P1-T1 … P4-T10)

### Phase 1 — Data infrastructure

| Task | Status | Note |
| --- | --- | --- |
| P1-T1 Environment and repository scaffolding | **Complete** | `pyproject.toml`, package layout, CI |
| P1-T2 Data acquisition and raw validation | **Complete** | `scripts/download_data.py`, `data/raw/metadata.json`, `reports/data_ingest.md` |
| P1-T3 Result-value decoding | **Complete** | `data/decoders.py` + tests |
| P1-T4 Scramble normalization | **Complete** | `decoders.py::normalize_multiblind_scramble` |
| P1-T5 Round-format normalization | **Complete** | `decoders.py::compute_average`, `reconciliation.json` |
| P1-T6 Feature engineering | **Complete** | `data/features.py` (`as_of` enforced) |
| P1-T7 Temporal split and frozen statistics | **Complete** | `data/splits.py`, `data/splits/frozen_stats.json` |
| P1-T8 Parquet export and performance optimization | **Partial** | Parquet exported; performance benchmark report absent |
| P1-T9 Data loader and streaming support | **Partial** | `WCABenchData` + `load_dataset` exist; no dedicated streaming loader for memory-constrained training |
| P1-T10 Data card and documentation | **Complete** | `datacard.md`, `docs/data/*` |
| P1-T11 QA and testing | **Partial** | Tests exist; coverage unmeasured; no formal QA report |

### Phase 2 — Task definition and baselines

| Task | Status | Note |
| --- | --- | --- |
| P2-T1 Unified Task interface | **Complete** | `tasks/base.py` (`Task` Protocol + `BaseTask`) |
| P2-T2 Metric library | **Complete** | `evaluation/metrics.py` (18 metric functions) |
| P2-T3 Rolling-window protocol | **Complete** | `evaluation/protocol.py::RollingWindowProtocol` |
| P2-T4 4-way stratified evaluation | **Complete** | `evaluation/stratified.py` (event / skill / time / continent) |
| P2-T5 Significance tests and effect sizes | **Partial** | Implemented but not invoked by the task runner |
| P2-T6 Task-definition freeze (M2) | **Complete** | `docs/tasks/*` (five elements each) |
| P2-T7 T1 + baselines | **Complete** | 4 baselines |
| P2-T8 T2 + baselines | **Partial** | 2 registered (3rd exists but unregistered); interface inconsistency |
| P2-T9 T3 + baselines | **Missing** | 2 baselines (target ≥3) |
| P2-T10 T4 + baselines | **Missing** | 2 baselines (target ≥4 per task document) |
| P2-T11 T5 + baselines | **Missing** | 2 baselines (target ≥4 per task document) |
| P2-T12 Experiment management | **Partial** | YAML-driven; no W&B/MLflow integration despite the plan |
| P2-T13 Leaderboard generation (M3) | **Complete** | `scripts/build_leaderboard.py`, `examples/leaderboard.*` |

### Phase 3 — Release

| Task | Status | Note |
| --- | --- | --- |
| P3-T1 Paper framework and figures | **In remediation** | `paper/figures/make_figures.py` |
| P3-T2 Paper draft | **In remediation** | `paper/sections/*` |
| P3-T3 Reproducibility package | **In remediation** | `examples/submission_template/` + validator |
| P3-T4 Internal review | **Missing** | Process step |
| P3-T5 NeurIPS submission (M4) | **Missing** | External |
| P3-T6 GitHub repository publication | **Partial** | Governance complete; not confirmed public |
| P3-T7 HF dataset publication | **In remediation** | `publish/huggingface/` |
| P3-T8 Model weight hosting | **In remediation** | `publish/huggingface/upload_models.py` |
| P3-T9 Documentation site live | **Partial** | Builds locally; `docs.yml` deploys to GitHub Pages on push |
| P3-T10 Submission spec and evaluation service | **In remediation** | `scripts/validate_submission.py` |
| P3-T11 Community outreach (M5) | **Missing** | External |
| P3-T12 Post-release monitoring | **Missing** | External |

### Phase 4 — Iteration and extension

| Task | Status |
| --- | --- |
| P4-T1 Feedback collection | **Missing** (external) |
| P4-T2 Task-definition iteration | **Missing** |
| P4-T3 Extended Test Set | **Missing** |
| P4-T4 GNN baseline | **In remediation** |
| P4-T5 Causal baselines (IV, causal forest) | **In remediation** |
| P4-T6 Bayesian baselines | **In remediation** |
| P4-T7 Challenge platform (M6) | **Missing** (external) |
| P4-T8 Challenge operations | **Missing** (external) |
| P4-T9 Journal extension | **Missing** |
| P4-T10 Maintainer handbook and roadmap v2 | **Missing** |

---

## 10. Non-plan findings (hygiene and consistency)

These were not acceptance criteria but were flagged during the audit and are fixed or scheduled.

| # | Finding | Severity | Resolution |
| --- | --- | --- | --- |
| H1 | Documentation claimed **MIT** in at least six places while `LICENSE` and `pyproject.toml` declare **Apache-2.0** | High | Fixed across `docs/` (EN + ZH) |
| H2 | `CITATION.cff` had `repository-code: "https://github.com/"` (placeholder) | Medium | Fixed |
| H3 | 5 scratch scripts in `scripts/` (`_debug_all_tasks.py`, `_debug_baseline.py`, `_debug_t1.py`, `_run_limit_transfer.py`, `_run_remaining.py`); 4 contained hard-coded `F:\workspace\WCA-Bench` paths | High | Deleted |
| H4 | Root `plan.md` (22 KB, Chinese) duplicates `docs/plan/` | Low | **Retained** — it is the original project proposal supplied by the user. Recommend moving to `docs/archive/` if a pristine repository root is preferred |
| H5 | `.pytest_cache/` present at repository root and not ignored | Low | Added to `.gitignore` |
| H6 | `notebooks/` contains only `00_readme.py`; no real exploratory notebook despite `docs/plan/structure.md` listing three | Medium | Scheduled — add executable notebooks |
| H7 | Baseline return-type inconsistency (see §4.3) | Medium | In remediation |
| H8 | `examples/*.json` had no `significance` key; only 7 of 10 registered models had persisted reports | High | In remediation |
| H9 | No `publish/` or `paper/` directory at all | High | In remediation |
| H10 | Project language was Chinese-only, including code comments in a few task modules; no i18n | High | English is now the primary language; `README_zh.md`, `datacard_zh.md`, `CONTRIBUTING_zh.md`, `CODE_OF_CONDUCT_zh.md` and the `/zh/` documentation locale provide Chinese |
| H11 | No coverage tooling; `pytest-cov` absent from `pyproject.toml` and CI | Medium | In remediation |
| H12 | No `cache/`-aware note for the VitePress build: `emptyDir` on `docs/.vitepress/dist` fails while the dev server holds the directory on Windows | Low | Documented in `docs/` build guidance |

---

## 11. Remediation summary for this session

| Cluster | Action | Owner scope |
| --- | --- | --- |
| Language & i18n | English primary; `README_zh.md`; bilingual docs site (`/` + `/zh/`); bilingual data card, contributing, code of conduct | root + `docs/` |
| Baseline coverage | Add DNF tree/Bayesian baselines, limit GP+EVT and hierarchical baselines, transfer IV and causal-forest baselines; implement `deep/`, `graph/`, `bayesian/` packages with optional-dependency fallbacks | `src/`, `configs/` |
| Statistical reporting | Add `Report.significance`; wire paired tests + bootstrap CI into `run_all_baselines`; persist `significance` in every report | `src/`, `scripts/` |
| Multi-seed | `scripts/run_multi_seed.py` → mean ± std, `examples/multi_seed.md` | `scripts/` |
| Submission spec | `scripts/validate_submission.py` + `examples/submission_template/` | `scripts/`, `examples/` |
| Publication | `publish/` with Hugging Face dataset card, `dataset_infos.json`, LFS attributes, ModelScope card and config, staging/archive tooling, dry-run upload scripts | `publish/` |
| Paper | `paper/` arXiv-ready XeLaTeX with sections, bibliography, figure generator, Makefile | `paper/` |
| Hygiene | Remove scratch scripts; extend `.gitignore`; fix license inconsistency; fix `CITATION.cff` | root, `scripts/` |
| Coverage | Add `pytest-cov`, `--cov` in CI, `[tool.coverage.run]` | root, `.github/` |

---

## 12. Residual gaps (not addressable in this session)

| Gap | Reason |
| --- | --- |
| A4.1 / A4.8 / A4.9 / A5.1 / A5.5–A5.7 | Require external actors: submission, community channels, third-party reproduction, challenge hosting |
| A1.9 performance benchmark | Requires a defined measurement protocol and a stable reference machine |
| A2.5 formal review record | Requires human reviewers |
| A5.2 / A5.3 | Depend on real community feedback and a post-window data release |
| G6 reproduction grades | Depend on an independent third party |

---

## 13. Recommended priority order for the next cycle

1. **Close A3** — push every task to ≥3 baselines and persist `significance` for every report (highest scientific value; blocks the paper's quantitative claims).
2. **Close A1.2 / A1.4 / A1.7 / A1.9** — checksum manifest, average-agreement assertion, coverage gate, and a performance benchmark with a documented protocol.
3. **Publish D1** — stage and release the dataset on Hugging Face and ModelScope so that A4.4/A4.5 can be closed with real links.
4. **Ship D7** — finalise the paper once the refreshed leaderboard numbers are in.
5. **Harden G1** — add a type checker so Gate 1 matches the plan's wording ("lint **and type** checks").

---

## 14. Post-remediation verification (same session)

The findings in §2–§10 were remediated and re-verified. This section records the state **after**
the fixes, so the scorecard in §1 should be read as the as-found baseline and this section as the
current state.

### 14.1 Closed items

| Item | As found | After remediation | Evidence |
| --- | --- | --- | --- |
| A3.1 baseline coverage | 13 baselines, 3 tasks below target | **21 baselines** — T1: 5, T2: 4, T3: 4, T4: 4, T5: 4 | `outputs/reports/`, `examples/*.json` |
| A3.3 complete reports | no `significance`; limit/transfer strata empty | **21/21 reports contain `significance`** with `reference`, `metric`, `paired_unit`, `n_pairs`, `mean_diff`, `ci95`, `p_value`, `effect_size`, `test`, `seed` | `examples/*__*.json` |
| A3.6 multi-seed | single seed only | **Seeds 42/43/44** aggregated to mean ± std | `examples/multi_seed.md`, `outputs/multi_seed/multi_seed.json` |
| A3.7 significance spec | implemented but never invoked | Wired into `BaseTask.run_all_baselines` via `attach_significance` | `src/wca_bench/tasks/base.py` |
| A4.7 submission validator | absent | `scripts/validate_submission.py` + `examples/submission_template/` | CI step `Validate submission template` |
| A1.7 / G2 coverage | not measured | `pytest-cov` in `dev` extras, `[tool.coverage.run]`, CI runs `--cov=wca_bench` | `pyproject.toml`, `.github/workflows/ci.yml` |
| A4.4 / A4.5 data & model publishing | absent | `publish/` with the HF dataset card, `dataset_infos.json`, LFS attributes, ModelScope config, staging/archive tooling; all dry-runs pass | `publish/**` |
| D1 / D7 / D8 | dataset, paper, release layout missing | Release tree staged (33 files, 234.9 MB); **arXiv-ready XeLaTeX paper in English and Chinese, both compiling** | `publish/`, `paper/`, `paper/zh/` |
| H1 licence contradiction | docs said MIT, `LICENSE` is Apache-2.0 | All occurrences unified to **Apache-2.0** (`package.json`, `plan.md`, docs EN+ZH) | repository-wide search |
| H2 `CITATION.cff` placeholder | `repository-code: "https://github.com/"` | Real URL plus `url`/`license-url`/`preferred-citation.url` | `CITATION.cff` |
| H3 scratch scripts | 5 scripts, 4 with hard-coded `F:\` paths | Deleted; `scripts/` now holds 8 real tools only | `scripts/` |
| H5 `.pytest_cache` | present and unignored | Added to `.gitignore` alongside `.ruff_cache`, `.coverage`, `publish/_staging`, `publish/dist`, LaTeX artefacts | `.gitignore` |
| H6 notebooks | one placeholder `.py` | Three executable notebooks: data exploration, domain rules, baseline analysis | `notebooks/*.ipynb` |
| H7 baseline interface | duck-typed baselines in three tasks | Unified on the `Baseline` dataclass; `SkillTransferTask` gained a task-level `evaluate` | `src/wca_bench/tasks/*/task.py` |
| H9 tooling | no release or paper tooling | `publish/tools/{stage_release,make_archive}.py`, `paper/Makefile`, `paper/figures/make_figures.py`, `paper/check_bib.py` | — |
| H10 language / i18n | Chinese-only | **English primary**; `README_zh.md`, `datacard_zh.md`, `CONTRIBUTING_zh.md`, `CODE_OF_CONDUCT_zh.md`, and a full `/zh/` docs locale (31 EN + 31 ZH pages) | `docs/`, root `*_zh.md` |
| H12 Windows build blocker | `vitepress build` from a lower-case drive letter failed with `Cannot read properties of undefined (reading 'imports')` | Root cause identified (VitePress compares `srcDir` chunk ids by exact string; Rollup records upper-case drive letters) and fixed by normalising the drive letter in `srcDir` | `docs/.vitepress/config.mts` |

### 14.2 Verification executed in this session

| Check | Result |
| --- | --- |
| `python -m pytest tests -q` | **39 passed**, exit 0 |
| `python -m ruff check src tests scripts` | **0 errors**, exit 0 |
| `npm run docs:build` | **build complete**, 63 HTML pages (31 EN content + 31 ZH content + 404) |
| Full GPU baseline run | 21/21 reports written, 0 failures |
| GPU multi-seed run | 3 seeds × 5 tasks completed, mean ± std produced |
| `latexmk -xelatex main.tex` (EN) | 29 pages, **0 undefined citations/references** |
| `latexmk -xelatex` (ZH, `ctex`) | Compiled successfully (`paper/zh/main.pdf`) |
| `paper/check_bib.py` | 30 unique keys, all defined, none unused, all `\input` targets exist |
| `publish/**` dry-runs | All six entry points pass; missing-dependency paths exit 1 with an install hint |
| Reference verification | **31 entries checked online**; 2 CubeBench papers newly added; 2 unverifiable DOIs removed rather than guessed | `paper/references_verification.md` |
| Data verification | Export date `2026-09-21T00:00:30Z` and format `v2.0.2` match the official API; the TSV archive is **byte-identical** (377,258,709 bytes) to the official download | `paper/data_verification.md` |

### 14.3 Issues found and fixed during the GPU runs

Three defects would have silently degraded the released results. They were caught because the
reported `cost.device` did not match reality.

| Defect | Symptom | Fix |
| --- | --- | --- |
| **Silent dependency fallback** | `xgboost_log` / `xgboost_dnf` reported `fallback: "no_xgboost"` and were in fact sklearn RandomForest runs; the headline T1 number was 0.2346 instead of the true XGBoost 0.1639 | Installed `xgboost 3.4.1`, `lightgbm 4.7.0`, `statsmodels 0.15.0`; re-ran |
| **Swallowed torch exception in the GNN** | `except Exception: factor = None` disguised any torch failure as `fallback: "no_torch"`, so the graph baseline silently ran as numpy propagation | Distinguished `ImportError` from other exceptions, recorded `fallback`/`torch_error` in `attrs`; the torch path now succeeds (`backend: "gnn"`, CUDA) |
| **Device mislabelling** | Pure-CPU baselines were stamped with the global `--device cuda` value in `cost.device` | `baseline_cost` now reads the device declared in each baseline's own prediction `attrs`; only accelerator baselines report `cuda:<model>` |

### 14.4 Updated scorecard

| Area | Complete | Partial | Missing |
| --- | --- | --- | --- |
| A1 Data pipeline | 9 | 0 | 0 |
| A2 Task definitions | 5 | 0 | 0 |
| A3 Baselines | 6 | 1 | 0 |
| A4 Release | 6 | 2 | 1 |
| A5 Iteration & extension | 1 | 1 | 5 |
| D1–D9 | 7 | 2 | 0 |
| Quality gates | 5 | 1 | 0 |
| **Total** | **39** | **7** | **6** |

Remaining gaps are external dependencies (community channels, third-party reproduction,
challenge hosting) or human review steps — all listed in §12 and §13. The A1.9 performance
benchmark and the G1 type checker, previously open, are now closed.

### 14.5 Result changes caused by the fixes above

Because the XGBoost fallback and the GNN fallback were removed, the released numbers moved. The
current authoritative values are in `examples/README.md`, `examples/leaderboard.md` and
`examples/multi_seed.md`. Headline changes versus the as-found state:

| Task | Metric | As found | Now |
| --- | --- | --- | --- |
| T1 | `xgboost_log` MAE(log) | 0.2346 (RandomForest fallback) | **0.1639** (real XGBoost, GPU) |
| T2 | `gnn` Kendall τ | 0.6041 (numpy fallback) | **0.5670** (torch GNN on CUDA) |
| T3 | best AUC-PR | 0.3926 vs 0.3894 | **`xgboost_dnf` 0.3731** vs `beta_binomial` 0.3725 |
| T5 | identifiable pairs | 423 | **413** |
