# Development Plan · Overview

This chapter is the **detailed development plan** for WCA-Bench, covering directory organization, documentation layering, phase breakdown, milestones, the work breakdown structure (WBS), dependencies, and acceptance criteria, for review and subsequent execution.

## 1. Plan Structure

| Chapter | Contents |
| --- | --- |
| [Directory Organization and Documentation Layering](/plan/structure) | GitHub repository structure, module responsibilities, documentation layering system |
| [Phase Breakdown and Milestones](/plan/roadmap) | 12-month, four-phase roadmap and milestones M1–M6 |
| [Phase 1: Data Infrastructure](/plan/phase-1) | Task breakdown for months 1–3 |
| [Phase 2: Task Definition and Baselines](/plan/phase-2) | Task breakdown for months 4–6 |
| [Phase 3: Benchmark Release](/plan/phase-3) | Task breakdown for months 7–9 |
| [Phase 4: Iteration and Expansion](/plan/phase-4) | Task breakdown for months 10–12 |
| [Dependencies](/plan/dependencies) | Inter-task prerequisites, critical path, external dependencies |
| [Acceptance Criteria](/plan/acceptance) | Acceptance criteria for the phases and for final delivery |
| [Risks and Mitigation](/plan/risks) | Data / saturation / community / ethical risks |
| [Publication Strategy](/plan/publication) | Paper targets and the publication roadmap |

## 2. Timeline at a Glance

```text
Months 1–3    Phase 1 ██████████  Data infrastructure
Months 4–6    Phase 2 ██████████  Task definitions and baselines
Months 7–9    Phase 3 ██████████  Benchmark release and community building
Months 10–12  Phase 4 ██████████  Iteration and expansion

Milestones:  M1(month 3)   M2(month 5)  M3(month 6)   M4(month 7)  M5(month 9)   M6(month 12)
```

## 3. Task Numbering Convention

```text
P<phase>-T<index>    e.g. P1-T3 = the 3rd task of phase 1
M<n>                 milestone, e.g. M2 = baselines complete in month 5
D<n>                 deliverable, e.g. D3 = data card
```

## 4. Roles (Suggested)

| Role | Responsibilities |
| --- | --- |
| Principal investigator (PI) | Overall direction, paper writing, community liaison |
| Data engineer | Data pipeline, storage optimization, data card |
| ML engineer ×2 | Task adaptation, baseline implementation, experiment management |
| Statistics / causal expert | Statistical testing, Bayesian and causal methods |
| Documentation / community maintainer | Documentation site, submission specification, community operations |

## 5. Working Practices

| Mechanism | Convention |
| --- | --- |
| Version control | GitHub, with `main` as the trunk plus feature branches |
| Code review | Every merge requires a PR and at least one reviewer |
| Continuous integration | GitHub Actions runs tests and a small-sample end-to-end pipeline |
| Task tracking | GitHub Issues + Projects (kanban board) |
| Experiment logging | W&B / MLflow, with configs stored in `configs/` |
| Documentation sync | This VitePress site is updated together with the code repository |

## 6. Further Reading

- [Directory Organization and Documentation Layering →](/plan/structure)
- [Phase Breakdown and Milestones →](/plan/roadmap)
- [Dependencies →](/plan/dependencies)
- [Acceptance Criteria →](/plan/acceptance)
