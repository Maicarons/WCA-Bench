# WCA-Bench

**A standardized sports-analytics benchmark built on the World Cube Association results database.**

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)](pyproject.toml)
[![Tasks](https://img.shields.io/badge/tasks-5-brightgreen.svg)](#the-five-tasks)
[![Baselines](https://img.shields.io/badge/baselines-multi--family-orange.svg)](#baselines-and-example-results)
[![Docs](https://img.shields.io/badge/docs-VitePress-42b883.svg)](docs/)
[![Paper](https://img.shields.io/badge/paper-arXiv%20XeLaTeX-b31b1b.svg)](paper/)
[![中文文档](https://img.shields.io/badge/lang-%E4%B8%AD%E6%96%87-red.svg)](README_zh.md)

WCA-Bench is the first comprehensive machine-learning benchmark built on the **full public competition record of the World Cube Association (WCA)**. It defines five core tasks — result prediction, placement prediction, DNF prediction, human-limit estimation, and skill-transfer analysis — together with a leakage-free evaluation protocol and a reproducible experimental framework for sports analytics.

---

## Table of contents

- [Why WCA-Bench](#why-wca-bench)
- [Key features](#key-features)
- [Quick start](#quick-start)
- [Repository layout](#repository-layout)
- [The five tasks](#the-five-tasks)
- [Evaluation protocol](#evaluation-protocol)
- [Baselines and example results](#baselines-and-example-results)
- [Data](#data)
- [Reproducibility](#reproducibility)
- [Documentation](#documentation)
- [Publishing](#publishing)
- [Paper](#paper)
- [Citation](#citation)
- [License and data attribution](#license-and-data-attribution)
- [Contributing](#contributing)

---

## Why WCA-Bench

Machine-learning research on WCA data suffers from three problems:

1. **Fragmentation.** Existing work targets single tasks (kernel-density placement prediction, linear-regression world-record extrapolation, Gaussian-process plus extreme-value human-limit estimation) with mutually incompatible splits, metrics, and preprocessing, so numbers cannot be compared.
2. **No standardized evaluation.** The *CubeBench* family of benchmarks evaluates **cube solving** — the spatial reasoning and sequence-planning ability of LLM agents. It says nothing about predictive or inferential ability on real competition data.
3. **Domain-specific structure ignored.** WCA data has properties that generic time-series models cannot handle without explicit rule modelling: longitudinal careers, cross-event skill transfer, round formats (average of 5, mean of 3), sentinel encodings (`-1` DNF, `-2` DNS), multi-blind encodings (`1SSAATTTTT` / `0DDTTTTTMM`), and outlier-trimming rules that amplify the effect of a single DNF.

WCA-Bench is **not** a new prediction model. It defines an evaluation question: *under the real constraints of competitive sports data, how do different methodological families (classical statistics, deep learning, graph learning, generative models) compare?*

| Dimension | CubeBench family | **WCA-Bench** |
| --- | --- | --- |
| Data source | Synthetic scramble states | Real WCA competition records |
| Evaluation target | Spatial reasoning & sequence planning | Predictive and inferential ability on sports data |
| Task types | Solving, move-count optimization | Regression, ranking, classification, extreme-value estimation, causal inference |
| Time dimension | Static states | Longitudinal career tracking (2003–2026) |
| Domain rules | Cube move semantics | WCA competition rules and encodings |
| Evaluated systems | LLM agents | Statistical, ML, and DL models |

---

## Key features

| Dimension | What WCA-Bench provides |
| --- | --- |
| **Data** | Official WCA Results Export v2.0.2 — ~6.9M results, ~298k persons, ~18.7k competitions, 17 active events plus retired events |
| **Tasks** | Five tasks spanning a continuous difficulty spectrum from regression to causal inference |
| **Protocol** | Temporal split plus rolling-window evaluation with frozen benchmark statistics — no future leakage |
| **Stratification** | Four-dimensional stratified reporting: by event, skill level, time slice, and continent |
| **Statistics** | Paired *t*-tests, bootstrap confidence intervals, Friedman + Nemenyi, Cohen's *d* / Cliff's *delta* |
| **Baselines** | Statistical, tree-based, deep, graph, Bayesian, and causal families, all runnable through one interface |
| **Reproducibility** | Fixed seeds, YAML-driven experiments, offline synthetic data path, submission validator |
| **Governance** | Data card with allowed/prohibited uses, contributor guidelines, code of conduct, CITATION |
| **i18n** | English primary documentation with a full Simplified-Chinese locale (`README_zh.md`, `/zh/` docs) |

---

## Quick start

### Install

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
# source .venv/bin/activate       # macOS / Linux

# core + dev + optional accelerators
pip install -e ".[dev,fast,boost]"
```

Optional heavy extras:

```bash
pip install -e ".[deep]"          # torch-based sequence/graph baselines
```

### Offline end-to-end (synthetic data — used by CI)

```bash
python scripts/generate_synthetic.py --small
python scripts/build_dataset.py --source synthetic
python scripts/run_all_baselines.py --mode small
python scripts/build_leaderboard.py
pytest
```

### Real WCA data

```bash
python scripts/download_data.py                 # fetch the official TSV export
python scripts/build_dataset.py --source raw    # decode, featurize, split, freeze stats
python scripts/run_all_baselines.py --mode full
python scripts/build_leaderboard.py
```

Build the documentation site:

```bash
npm install
npm run docs:dev      # http://localhost:5173
npm run docs:build    # static site -> docs/.vitepress/dist
```

---

## Repository layout

```text
wca-bench/
├── src/wca_bench/          # Python package
│   ├── data/               # loaders, decoders, features, splits, synthetic generator
│   ├── tasks/              # unified Task interface + T1–T5 adapters
│   ├── baselines/          # statistical / tree / deep / graph / bayesian / causal
│   ├── evaluation/         # metrics, rolling protocol, stratification, significance
│   ├── leaderboard/        # report aggregation
│   └── utils/              # io, logging, seeding
├── configs/                # YAML experiment configs (one per baseline)
├── scripts/                # download, build, run, validate, leaderboard
├── tests/                  # unit + integration tests
├── docs/                   # VitePress documentation site (English + zh locale)
├── examples/               # baseline reports, leaderboard, submission template
├── publish/                # Hugging Face + ModelScope release assets and scripts
├── paper/                  # arXiv-ready XeLaTeX paper
├── datacard.md             # dataset card
├── LICENSE                 # Apache-2.0
└── pyproject.toml
```

---

## The five tasks

| ID | Task | Learning paradigm | Primary metrics | Domain challenge |
| --- | --- | --- | --- | --- |
| **T1** | Result prediction | Regression | MAE / RMSE in log space, interval coverage | Non-stationary careers; large variance differences across events |
| **T2** | Placement prediction | Ranking | Kendall's τ, top-3 overlap, Brier score | Competitor interaction effects; trimming rules amplify DNF impact |
| **T3** | DNF prediction | Imbalanced classification | AUC-ROC, AUC-PR, F1, MCC, calibration | Rare events, extremely uneven across events, sequence dependence |
| **T4** | Human-limit estimation | Extreme-value / extrapolation | Leave-one-out stability, interval coverage, domain agreement | Extrapolation risk; vastly different data density per event |
| **T5** | Skill-transfer analysis | Causal inference | Point-estimate precision, robustness, expert agreement | Confounding; non-random event participation order |

Every task follows one interface:

```python
class Task(Protocol):
    name: str
    task_type: TaskType

    def split(self) -> dict[str, pd.DataFrame]: ...
    def featurize(self, as_of) -> pd.DataFrame: ...   # `as_of` is mandatory: leakage guard
    def metrics(self) -> list[str]: ...
    def baselines(self) -> list[Baseline]: ...
    def evaluate(self, model_name: str, preds=None) -> Report: ...
```

Because `featurize` requires an explicit `as_of`, it is impossible to build features that use information from the decision moment onward.

---

## Evaluation protocol

**Temporal split (not random):**

| Split | Window | Purpose |
| --- | --- | --- |
| train | 2003–2022 | Fitting and benchmark-statistic estimation |
| validation | 2023–2024 | Hyper-parameter tuning and model selection |
| test | 2025–2026 | Final evaluation (frozen window) |

**Rolling-window evaluation.** For every test competition, a model may use only records strictly earlier than that competition. Benchmark statistics — historical means, world records, skill-level quantile thresholds — are computed once from the training window and then **frozen** for the whole test period.

**Four-dimensional stratification** avoids conclusions being dominated by the largest subgroup: by event, by skill level (novice / intermediate / advanced / elite), by time slice (Test-A 2025H1, Test-B 2025H2, Test-C 2026H1), and by continent.

**Statistical rigour.** All model comparisons report paired *t*-tests, 1000-sample bootstrap confidence intervals, Friedman + Nemenyi for multi-model comparison, and effect sizes (Cohen's *d* or Cliff's *delta*).

**Hard subsets.** To guard against benchmark saturation, each task additionally reports a hard subset (for example, DNF prediction reports players whose historical DNF rate lies in `[0.1, 0.3]`).

See [`docs/evaluation/`](docs/evaluation/) for the full protocol.

---

## Baselines and example results

**21 baselines** across six families are all reached through the same `Task.evaluate` path:

| Family | Baselines | Coverage |
| --- | --- | --- |
| `statistical` | historical mean, Gaussian KDE, Psych Sheet, Plackett–Luce, KDE placement simulation, historical DNF rate, exponential decay, changepoint, GP + extreme-value | T1–T5 |
| `tree` | ridge on `log(best)`, XGBoost regression, logistic regression, XGBoost DNF classifier | T1, T3 |
| `deep` | LSTM sequence model *(optional torch, graceful fallback)* | T1 |
| `graph` | player–competition heterogeneous GNN *(optional torch, graceful fallback)* | T2 |
| `bayesian` | Beta–Binomial DNF model, hierarchical shrinkage limit estimation | T3, T4 |
| `causal` | Spearman correlation reference, difference-in-differences, instrumental variables (2SLS), causal forest | T5 |

Sample-run results on the real WCA export v2.0.2 (sampled test window, seed 42, **CUDA**) are
reported in [`examples/leaderboard.md`](examples/leaderboard.md); multi-seed means are in
[`examples/multi_seed.md`](examples/multi_seed.md).

| Task | Best sampled baseline | Primary metric | Multi-seed (42/43/44) |
| --- | --- | --- | --- |
| T1 Result prediction | `xgboost_log` | MAE(log) ↓ 0.164 | 0.106 ± 0.042 |
| T2 Placement prediction | `kde_simulation` / `plackett_luce` / `psych_sheet` | Kendall τ ↑ 0.767 | 0.813 ± 0.034 |
| T3 DNF prediction | `xgboost_dnf` | AUC-PR ↑ 0.373 | `beta_binomial` 0.294 ± 0.057 |
| T4 Human limit | `gp_evt` | leave-one-out stability ↓ 0.98 | 0.984 ± 0.000 |
| T5 Skill transfer | `spearman_correlation` | 413 identifiable event pairs | 413 |

Two findings worth noting:

1. **Domain-aware baselines beat generic deep and graph models.** On T1 the LSTM
   (MAE(log) 0.944 ± 0.075) is far behind gradient-boosted trees (0.106 ± 0.042); on T2 the GNN
   (τ 0.744 ± 0.126) trails the rule-aware Psych Sheet baseline (0.813 ± 0.034).
2. **Close contenders reorder across evaluation windows.** On T3 the single run favours
   `xgboost_dnf` (0.373) while the multi-seed mean favours `beta_binomial` (0.294 ± 0.057 vs
   0.278 ± 0.072) — which is precisely why multi-seed reporting is required.

### Compute and hardware

- Tabular baselines (KDE, Plackett–Luce, Beta–Binomial, GP + EVT, DID/IV, causal forest) run on
  **CPU** by design: the working set is 2k–80k rows and the bottleneck is the per-competition
  small-batch forward pass plus rule decoding, which is latency-bound rather than throughput-bound.
- The **LSTM and GNN baselines train on CUDA**, and the boosting baselines can be placed on the GPU
  too. The results above were produced on an **NVIDIA GeForce RTX 4060 Laptop GPU (8 GB)**,
  CUDA 13.0, torch 2.13.0+cu130.
- Every report records the device actually used: `device` (`cpu` or `cuda:<model>`),
  `wall_clock_sec`, `cpu_hours`, and — on the GPU — `gpu_hours` and `gpu_model`.
- Select the device with `--device {auto,cpu,cuda}` or `WCA_BENCH_DEVICE`; the default stays `cpu`
  so that small runs remain bit-for-bit reproducible.

> Full leaderboards must be re-run on the complete dataset under the rolling-window protocol. The numbers above come from a tractable sampling mode and are labelled as such.

---

## Data

WCA-Bench ships two data paths:

- **Real data** — `scripts/download_data.py` fetches the official WCA Results Export (v2.0.2). `scripts/build_dataset.py --source raw` decodes results, normalizes round formats, builds features, applies the temporal split, and freezes benchmark statistics. Outputs land in `data/processed/` and `data/splits/` as Parquet.
- **Synthetic data** — `scripts/generate_synthetic.py` produces a small WCA-like export so that CI and offline development need no network access.

Decoding rules are explicit and testable: `time` values are centiseconds, `number` values are move counts, multi-blind results use the `1SSAATTTTT` / `0DDTTTTTMM` encodings, `-1` is DNF, `-2` is DNS, and `0` means no result. Average-of-5 reconstruction applies the official trim-best-and-worst rule.

Every usage constraint is documented in [`datacard.md`](datacard.md) — including prohibited uses such as gambling or betting prediction, discriminatory profiling, and any impersonation of official bodies.

---

## Reproducibility

- All experiments are driven by YAML files in [`configs/`](configs/) and can be re-run with a single command.
- Random seeds are fixed (`utils/seed.py`) and recorded in every report.
- Multi-seed runs are supported: `python scripts/run_multi_seed.py --seeds 42 43 44 --mode small`.
- Reports follow one schema: `overall`, `stratified`, `hard_subset`, `significance`, `cost`, `extras`.
- Submissions are checked with `python scripts/validate_submission.py <submission_dir>`; a skeleton lives in `examples/submission_template/`.
- Reproduction levels are defined as **L1** (re-runnable), **L2** (results within tolerance), and **L3** (raw predictions downloadable and metrics independently recomputable). The main leaderboard requires L3.

---

## Documentation

The documentation site is built with **VitePress** and is bilingual.

| Layer | English | 中文 |
| --- | --- | --- |
| Project proposal | `docs/guide/` | `docs/zh/guide/` |
| Technical design | `docs/data/`, `docs/tasks/`, `docs/evaluation/` | `docs/zh/...` |
| Development plan | `docs/plan/` | `docs/zh/plan/` |

Start with [`docs/guide/`](docs/guide/) (proposal) and [`docs/plan/`](docs/plan/) (development plan, milestones, dependencies, acceptance criteria).

---

## Publishing

Release assets for both major model hubs live in [`publish/`](publish/):

```bash
python publish/tools/stage_release.py --tier core --dry-run   # assemble the release tree
python publish/huggingface/upload_dataset.py --dry-run        # Hugging Face Hub
python publish/modelscope/upload.py --dry-run                 # ModelScope
python publish/tools/make_archive.py                          # tar.gz + SHA256SUMS
```

Tokens are read from `HF_TOKEN` and `MODELSCOPE_API_TOKEN` environment variables and are never written to disk.

---

## Paper

An arXiv-ready XeLaTeX manuscript is provided in [`paper/`](paper/):

```bash
cd paper
make            # or: latexmk -xelatex main.tex
make figures    # regenerate figures from examples/leaderboard.csv
```

See [`paper/README.md`](paper/README.md) for the TeX Live package list and packaging instructions.

---

## Citation

```bibtex
@misc{wcabench2026,
  title        = {WCA-Bench: A Sports Analytics Benchmark from World Cube Association Competition Data},
  author       = {{WCA-Bench Project}},
  year         = {2026},
  version      = {0.1.0},
  howpublished = {\url{https://github.com/Maicarons/WCA-Bench}},
  note         = {Dataset and benchmark}
}
```

Machine-readable metadata is in [`CITATION.cff`](CITATION.cff).

---

## License and data attribution

- **Code** is released under the [Apache License 2.0](LICENSE).
- **Data** is owned and maintained by the World Cube Association. Any redistribution of information derived from the WCA export must carry the official attribution:

  > This information is based on competition results owned and maintained by the World Cube Association, published at https://worldcubeassociation.org/results

- Usage constraints — including prohibited applications — are specified in [`datacard.md`](datacard.md).

---

## Contributing

Contributions are welcome. Please read [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) first.

Key rules:

- Dependency direction is one-way: `tasks → data`, `baselines → tasks → data`, `evaluation → tasks + data`, `leaderboard → evaluation`. The `data` package must never import from `tasks`, `baselines`, `evaluation`, or `leaderboard` (enforced by `tests/unit/test_import_policy.py`).
- Every pull request must pass lint, unit tests, the synthetic end-to-end run, the documentation build, and the leakage assertions.
- Any change to a task definition or the evaluation protocol must be reflected in `docs/` in the same pull request.

---

[English](README.md) · [简体中文](README_zh.md)
