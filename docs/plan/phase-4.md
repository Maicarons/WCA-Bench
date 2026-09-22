# Phase 4: Iteration and Expansion (Months 10–12)

> **Objective**: Iterate on the benchmark based on community feedback, expand method coverage, organize a challenge, and plan a journal version.
> **Exit milestone**: [M6 Community Challenge](/plan/roadmap#m6-·-community-challenge-month-12)

## 1. Phase Objectives

- Refine the task definitions based on community feedback
- Add more baseline methods (graph neural networks, causal inference methods)
- Organize the WCA-Bench challenge
- Prepare a journal extension

## 2. Work Breakdown (WBS)

| Task ID | Task name | Weeks | Prerequisites | Deliverables |
| --- | --- | --- | --- | --- |
| P4-T1 | Community feedback collection and triage | W37–W38 | M5 | Feedback list with priorities |
| P4-T2 | Task definition iteration (versioned) | W38–W40 | P4-T1 | v1.1 task definitions and changelog |
| P4-T3 | Extended test set release | W38–W39 | P4-T1 | Extended Test Set (2026 H2 and later) |
| P4-T4 | GNN baseline enhancement | W39–W42 | P4-T2 | Graph model baselines and results |
| P4-T5 | Causal method baseline enhancement | W40–W43 | P4-T2 | Complete IV / causal forest implementations |
| P4-T6 | Bayesian method baseline enhancement | W40–W43 | P4-T2 | Hierarchical Bayesian / EVT baselines |
| P4-T7 | Challenge platform setup (M6) | W43–W46 | P4-T2, P4-T3 | Kaggle competition page |
| P4-T8 | Challenge operation and results analysis | W46–W48 | P4-T7 | Results analysis report |
| P4-T9 | Journal extension planning | W45–W48 | P4-T8 | Journal paper proposal |
| P4-T10 | Long-term maintenance mechanism | W47–W48 | M6 | Maintainer handbook, roadmap v2 |

> Weeks continue from Phase 3 (W37 = the project's 37th week); the phase lasts 12 weeks (W37–W48).

## 3. Detailed Task Descriptions

### P4-T1 · Community Feedback Collection and Triage

- Aggregate feedback from GitHub Issues, discussions, and community channels
- Classify: task definitions / evaluation protocol / data quality / tooling usability
- Prioritize (impact × implementation cost)
- **Acceptance**: an actionable feedback list is produced

### P4-T2 · Task Definition Iteration (Versioned)

- Follow the principle of **versioned changes**: do not break the comparability of the existing leaderboard
- Change types:
 | Type | Handling |
 | --- | --- |
 | Clarifying (no semantic change) | Update directly, patch version |
 | Additive (new metrics/subsets) | Minor version; primary metrics unchanged |
 | Breaking (changes inputs/outputs) | Major version; a separate leaderboard |
- **Acceptance**: v1.1 definitions + changelog published

### P4-T3 · Extended Test Set Release

- Treat data from the second half of 2026 onward as the **Extended Test Set**
- The main leaderboard remains based on the fixed test window; the extended set is reported separately
- **Acceptance**: the extended set is loadable through the same interface

### P4-T4 ~ P4-T6 · Method Baseline Enhancement

| Task | New baselines | Goal |
| --- | --- | --- |
| P4-T4 | Competitor–competition heterogeneous GNN | Improve interaction modeling for T2 placement prediction |
| P4-T5 | Complete implementations of instrumental variables and causal forest | Strengthen causal identification for T5 |
| P4-T6 | Hierarchical Bayesian, Bayesian EVT | Strengthen uncertainty modeling for T3/T4 |

- **Acceptance**: the new baselines are added to the leaderboard with significance comparisons against existing baselines

### P4-T7 · Challenge Platform Setup (M6)

- Launch a competition on Kaggle (suggested main track: T1 or T2)
- Provide a baseline starter kit, evaluation scripts, and the submission format
- State the rules and ethical constraints clearly (gambling use prohibited)
- **Acceptance**: the competition page is live and accepts submissions

### P4-T8 · Challenge Operation and Results Analysis

- Monitor the leaderboard, answer questions, and prevent test-set leakage
- Produce a post-competition analysis report: characteristics of winning methods and methodological insights
- **Acceptance**: the analysis report is published

### P4-T9 · Journal Extension Planning

- Target journals: *Journal of Quantitative Analysis in Sports* / *Machine Learning*
- Content: systematically evaluate the performance gap between classical statistical methods and deep learning methods on WCA-Bench
- **Acceptance**: journal paper proposal and task assignments

### P4-T10 · Long-Term Maintenance Mechanism

- Maintainer handbook (release process, versioning strategy, review standards)
- Roadmap v2 (new task ideas: schedule optimization, advancement rule design, etc.)
- **Acceptance**: the handbook and roadmap are published

## 4. Phase Deliverables

| ID | Deliverable | Corresponding tasks |
| --- | --- | --- |
| D9 | Challenge and results analysis | P4-T7, P4-T8 |
| — | Task definition v1.1 + changelog | P4-T2 |
| — | Extended test set | P4-T3 |
| — | Additional method baselines | P4-T4 ~ P4-T6 |
| — | Maintainer handbook and roadmap v2 | P4-T10 |

## 5. Phase Acceptance Criteria

- [ ] ≥ 80% of the high-priority items in the community feedback list are completed
- [ ] Task definition iteration follows the versioning principle and does not break the existing leaderboard
- [ ] The extended test set is loadable and results are reported separately
- [ ] ≥ 3 new classes of method baselines are added to the leaderboard
- [ ] The challenge is live with participating teams (M6)
- [ ] The post-competition analysis report is published
- [ ] The journal paper proposal is complete

## 6. Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Conflicting feedback | Iteration direction wavers | Use "does it increase the scientific value of the benchmark?" as the criterion |
| Test-set leakage in the challenge | Distorted results | Hide test labels + limit submission frequency |
| Breaking changes | Leaderboard discontinuity | Strict versioning; major changes get a separate leaderboard |
| Insufficient maintainer capacity | Project stalls | Establish a multi-maintainer mechanism and a handbook |

## 7. Further Reading

- [Dependencies →](/plan/dependencies)
- [Acceptance Criteria →](/plan/acceptance)
- [Risks and Mitigation →](/plan/risks)
