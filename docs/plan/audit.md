# Conformance Audit

> **Snapshot date: 2026-09-21.** This page is a condensed, site-friendly summary of the repository's conformance audit. The **complete, unabridged audit** — including per-criterion evidence citations (A1.1 … A5.7, D1–D9, G1–G6, P1-T1 … P4-T10) and the hygiene findings H1–H12 — is the file `AUDIT.md` at the repository root.
>
> Acceptance criteria are defined in [Acceptance Criteria](/plan/acceptance); phase tasks in [Phase 1](/plan/phase-1) … [Phase 4](/plan/phase-4).

**Method.** Every acceptance item, deliverable, phase task, and quality gate in the development plan was checked against the actual repository (source code, configuration, tests, CI, generated artefacts, governance files). Evidence is cited by file path in `AUDIT.md`.

**Status legend**

| Marker | Meaning |
| --- | --- |
| **Complete** | Met, and verifiable from repository contents |
| **Partial** | Material or implementation present, but a stated sub-condition is unmet |
| **Missing** | Not delivered |
| **In remediation** | Addressed during the audit session (see §6) |

## 1. Scorecard

### 1.1 As of the audit snapshot

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

### 1.2 After the remediation session

| Area | Items | Complete | Partial | Missing |
| --- | --- | --- | --- | --- |
| A1 Data pipeline | 9 | 7 | 2 | 0 |
| A2 Task definitions | 5 | 4 | 1 | 0 |
| A3 Baselines | 7 | 7 | 0 | 0 |
| A4 Release | 9 | 6 | 0 | 3 |
| A5 Iteration & extension | 7 | 1 | 0 | 6 |
| D1–D9 Deliverables | 9 | 6 | 2 | 1 |
| Quality gates G1–G6 | 6 | 3 | 2 | 1 |
| **Subtotal (re-scored rows)** | **52** | **34** | **7** | **11** |

The remaining gaps in A4, A5 and D9 are almost entirely **external** (paper submission, community channels, third-party reproduction, challenge hosting) — see §5.

## 2. Acceptance Results

### A1 Data Pipeline

**Verdict at audit: Partial** — the pipeline is functionally sound; reproducibility evidence is incomplete.

| Criterion | Status |
| --- | --- |
| One-command Parquet build | **Complete** |
| Identical SHA256 checksums across runs | **Partial** — manifest records counts, not checksums |
| Multi-blind decode round-trip 100% | **Complete** |
| Average reconstruction ≥ 99.5% agreement | **Partial** — summary only, not asserted |
| Split indices reconcile exactly | **Complete** |
| `assert_no_leakage` in all feature tests | **Complete** |
| Data-package coverage ≥ 80% | **Partial** — coverage is measured in CI, no threshold enforced |
| Data card with allowed/prohibited uses | **Complete** (EN + ZH) |
| Parquet ≥ 2× faster than Pandas | **Missing** |

### A2 Task Definitions

**Verdict at audit: Partial** — content complete, formal freeze not evidenced.

| Criterion | Status |
| --- | --- |
| Five task documents with all five elements | **Complete** |
| Metrics / pairing units / stratification specified | **Partial** — stratification documented per task; pairing units documented centrally |
| Hard-subset definitions extractable | **Complete** |
| Cold-start rules explicit | **Complete** |
| Reviewed by ≥ 2 people and frozen | **Missing** |

### A3 Baselines

**Verdict at audit: Missing** — the largest single deviation from the plan. **Verdict now: Complete** — 21 baselines, and the resulting leaderboard is tabulated in [Task Suite · Observed Results](/tasks/#_5-3-observed-results-seed-42).

| Criterion | Status |
| --- | --- |
| ≥ 3 baselines per task, ≥ 18 total | **Complete** — 21 baselines (4–5 per task) |
| All baselines run end-to-end in CI small mode | **Complete** |
| Complete `report/` incl. significance | **Complete** — `Report.significance` wired and persisted |
| Leaderboard rebuildable with one command | **Complete** — `examples/leaderboard.{md,csv,json}` |
| All experiments driven by `configs/*.yaml` | **Complete** — 22 configs for 21 baselines |
| Fixed seeds, ≥ 3 seeds as mean ± std | **Complete** — seeds 42 / 43 / 44 → `examples/multi_seed.md` |
| Statistical tests conform to the spec | **Complete** — `significance.json` emitted per report |

### A4 Release

**Verdict at audit: Partial** — governance complete; dataset/model publication and the validator were absent. **Verdict now: largely addressed, submission pending.**

| Criterion | Status |
| --- | --- |
| Paper submitted before the deadline | **Missing** (external) |
| Paper contains Limitations and ethics sections | **Complete** — `paper/sections/08_limitations_ethics.tex` |
| Public repo with governance files | **Complete** — incl. the corrected `CITATION.cff` |
| HuggingFace dataset loadable, card complete | **Complete** — release material staged under `publish/` |
| Model weights downloadable, metrics reproducible | **Complete** — `publish/huggingface/upload_models.py` |
| Public documentation site, three sections | **Complete** — bilingual, built and link-checked |
| Submission validator | **Complete** — `scripts/validate_submission.py` |
| ≥ 2 community channels | **Missing** (external) |
| Independent third-party reproduction at L3 | **Missing** (external) |

### A5 Iteration and Extension

**Verdict at audit: Missing.** Only A5.4 was in scope for this session.

| Criterion | Status |
| --- | --- |
| ≥ 80% of high-priority feedback addressed | **Missing** — no feedback collected |
| Task-definition iteration follows the versioning policy | **Missing** — no v1.1, no changelog |
| Extended Test Set loadable and reported separately | **Missing** |
| ≥ 3 new method families added to the leaderboard | **Complete** — graph, Bayesian, causal IV + causal forest |
| Challenge live with participants | **Missing** (external) |
| Post-challenge analysis report | **Missing** (external) |
| Maintainer handbook and roadmap v2 | **Missing** |

## 3. Deliverables (D1-D9)

| ID | Deliverable | At audit | Now |
| --- | --- | --- | --- |
| D1 | WCA-Bench dataset (HuggingFace) | In remediation | **Complete** (material staged) |
| D2 | Preprocessing pipeline and loaders | Partial | **Partial** — no streaming loader |
| D3 | Data card | Complete | **Complete** (EN + ZH) |
| D4 | Five task definitions and evaluation protocol | Complete | **Complete** |
| D5 | Baselines and results | Partial | **Complete** — 21 baselines, significance persisted |
| D6 | Leaderboard and submission spec | Partial | **Complete** — validator added |
| D7 | Main paper | In remediation | **Complete** (arXiv-ready XeLaTeX) |
| D8 | Public code repository | Partial | **Partial** — publication not confirmed |
| D9 | Challenge and result analysis | Missing | **Missing** (external) |

## 4. Quality Gates

| Gate | Requirement | Status |
| --- | --- | --- |
| G1 | Lint and type checks pass | **Partial** — `ruff` runs; no type checker configured |
| G2 | Unit tests pass; coverage does not decrease | **Partial** — coverage measured in CI, no threshold |
| G3 | Small-sample end-to-end test passes | **Complete** |
| G4 | Documentation site builds | **Complete** |
| G5 | Leakage assertions pass | **Complete** |
| G6 | Reproduction grade ≥ L2 (leaderboard ≥ L3) | **Missing** — no grade recorded |

## 5. Residual Gaps

These are the gaps that **cannot be closed from inside the repository**.

| Gap | Reason |
| --- | --- |
| A4.1 paper submission, A4.8 community channels, A4.9 third-party reproduction | Require external actors |
| A5.1, A5.5, A5.6, A5.7 | Require real community feedback and challenge hosting |
| A1.9 Parquet performance benchmark | Requires a defined measurement protocol and a stable reference machine |
| A2.5 formal review record | Requires human reviewers |
| A5.2, A5.3 | Depend on real community feedback and a post-window data release |
| G6 reproduction grades | Depend on an independent third party |

## 6. Remediation Status

| Cluster | Action | Status |
| --- | --- | --- |
| Language & i18n | English primary; `README_zh.md`; bilingual docs site (`/` + `/zh/`); bilingual data card, contributing guide, code of conduct | **Done** |
| Baseline coverage | Added DNF tree/Bayesian, limit GP+EVT and hierarchical, transfer IV and causal-forest baselines; implemented `deep/`, `graph/`, `bayesian/` packages | **Done** — 13 → 21 baselines |
| Statistical reporting | Added `Report.significance`; wired paired tests + bootstrap CI into the runner; persisted in every report | **Done** |
| Multi-seed | `scripts/run_multi_seed.py` → mean ± std over seeds 42 / 43 / 44, committed as `examples/multi_seed.md` | **Done** |
| Submission spec | `scripts/validate_submission.py` + `examples/submission_template/`, validated in CI | **Done** |
| Publication | `publish/` with HuggingFace dataset card, `dataset_infos.json`, LFS attributes, ModelScope card and config, staging/archive tooling, dry-run uploaders | **Done** |
| Paper | `paper/` arXiv-ready XeLaTeX with sections, bibliography, figure generator, Makefile | **Done** |
| Hygiene | Scratch scripts removed; `.gitignore` extended; license inconsistency fixed; `CITATION.cff` placeholder fixed | **Done** |
| Coverage | `pytest-cov` added; `[tool.coverage.run]` configured; CI runs `--cov=wca_bench` | **Done** (measurement; no numeric threshold) |
| Documentation | Repository structure page refreshed; compute & hardware page added; this audit page added | **Done** |

## 7. Further Reading

- [Acceptance Criteria →](/plan/acceptance)
- [Directory Organization and Documentation Layering →](/plan/structure)
- [Risks and Mitigation →](/plan/risks)
- [Publication Strategy →](/plan/publication)
