# Project Scope

Clear boundaries are a prerequisite for the credibility of a benchmark. This chapter specifies what WCA-Bench **does** and **does not** do.

## 1. In Scope

### 1.1 Data Assets

- All core tables from the official public WCA database export (persons, competitions, results, result_attempts, scrambles, events, formats, round_types, countries, continents, championships)
- Preprocessed columnar artifacts (Parquet)
- Temporal split indices (train / val / test) and per-competitor longitudinal sequences

### 1.2 Task Suite

Five core tasks spanning a continuous difficulty spectrum from basic prediction to advanced inference:

| ID | Task | Type |
| --- | --- | --- |
| T1 | Result Prediction | Regression |
| T2 | Placement Prediction | Ranking |
| T3 | DNF Prediction | Classification (imbalanced) |
| T4 | Human Limit Estimation | Extreme value / extrapolation |
| T5 | Skill Transfer Analysis | Causal inference |

### 1.3 Evaluation and Engineering

- A leakage-free evaluation protocol (temporal splitting + rolling window)
- Four-dimensional stratified evaluation (event / competitor skill level / time / region)
- Statistical significance testing and effect size reporting
- Baseline implementations and unified experiment configuration management
- Data card, task documentation, and reproducibility checklist

## 2. Out of Scope

| Item | Reason |
| --- | --- |
| Cube solving / move-count optimization | Belongs to the CubeBench family and has objectives different from this benchmark |
| Spatial reasoning evaluation of LLM agents | See above; the evaluated subjects here are statistical/ML/DL models |
| Proposing a new state-of-the-art prediction model | This project is positioned as a benchmark and does not chase model leadership |
| Real-time live-competition prediction systems | An engineering product, outside the benchmark's remit |
| Inference about competitors' personal private data | Involves ethical risk and is explicitly prohibited |
| Prediction services for gambling / betting | Explicitly prohibited in the data card |
| Self-built data collection (crawling non-public data) | Only the official public WCA export is used |

## 3. Boundary Assumptions

1. **WCA data keeps being updated.** The test set is fixed to 2025–2026, and the main leaderboard is always based on that fixed window; data added later is released separately as an "Extended Test Set".
2. **Rule stability.** WCA competition regulations are assumed not to undergo breaking changes within the evaluation window; if they do, the change is recorded in the release notes and flagged separately.
3. **Language and regions.** The benchmark is released primarily in English, with bilingual (English/Chinese) documentation; country/region information follows the official WCA fields.
4. **Legal and licensing.** The code is released under the Apache-2.0 License; the data follows the WCA's acceptable use terms and is used for aggregate and statistical purposes only.

## 4. Forbidden Use Cases

> The following uses **violate** this project's data card terms:

- Any form of use for gambling, betting, or wager prediction
- Use for discriminatory screening, profiling, or ranking shaming of individual competitors
- Training content intended to impersonate official institutions or forge competition results
- Redistribution of individual-level data without removing personal identifiers

## 5. Delivery Boundaries

| Category | Delivery form |
| --- | --- |
| Code | Public GitHub repository (Apache-2.0) |
| Data | HuggingFace Datasets (preprocessed artifacts + split indices) |
| Weights | HuggingFace Models (baseline model weights) |
| Documentation | This VitePress site (proposal + technical design + development plan) |
| Paper | Submission to the NeurIPS 2026 Evaluations & Datasets Track |
| Community | Challenge and leaderboard |

## 6. Related Sections

- [Technical Approach Overview →](/guide/architecture)
- [Data Sources and Table Schemas →](/data/sources)
- [Evaluation Protocol and Stratification →](/evaluation/protocol)
