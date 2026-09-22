# Dependencies

This chapter presents the prerequisites between tasks, the critical path, and external dependencies, for scheduling and risk identification.

## 1. Dependency Overview

```text
P1-T1 Scaffolding
   │
P1-T2 Data acquisition
   │
P1-T3 Result decoding ──► P1-T5 Round normalization ──► P1-T6 Feature engineering
   │                                        │
P1-T4 Scramble normalization                ▼
                                        P1-T7 Temporal splitting
                                            │
                                            ▼
                                        P1-T8 Parquet export
                                            │
                                            ▼
                                        P1-T9 Data loader ──► M1
                                            │
                    ┌───────────────────────┘
                    ▼
              P2-T1 Task interface ──► P2-T2 Metrics library ──► P2-T3 Rolling protocol
                                                      │
                                          ┌───────────┼───────────┐
                                          ▼           ▼           ▼
                                      P2-T4 Stratify  P2-T5 Tests  (task implementations)
                                          │           │           │
                                          └─────┬─────┘           │
                                                ▼                 │
                                          P2-T6 Definition freeze (M2) ◄────┤
                                                                │
        P2-T7 ~ P2-T11 Five tasks and baselines ◄───────────────────┘
                    │
                    ▼
              P2-T13 Leaderboard (M3)
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
  P3-T2 Paper            P3-T6 Repository public
        │                       │
        ▼                       ├──► P3-T7 Dataset ──► P3-T10 Submission spec
  P3-T5 Submission (M4)         ├──► P3-T8 Model weights
                                └──► P3-T9 Documentation site
                                        │
                                        ▼
                                  P3-T11 Community outreach (M5)
                                        │
                                        ▼
                                  P4-T1 Feedback collection
                                        │
                    ┌───────────────────┼───────────────────┐
                    ▼                   ▼                   ▼
              P4-T2 Definition iterations  P4-T3 Extended test set  P4-T4~T6 Method enhancement
                    │                   │                   │
                    └───────────────────┼───────────────────┘
                                        ▼
                                  P4-T7 Challenge (M6) ──► P4-T8 Results analysis
```

## 2. Critical Path

**Critical path (determines the minimum project duration):**

```text
P1-T2 → P1-T3 → P1-T5 → P1-T6 → P1-T7 → P1-T8 → P1-T9
  → P2-T1 → P2-T2 → P2-T3 → P2-T6(M2) → P2-T7 → P2-T13(M3)
  → P3-T2 → P3-T5(M4) → P3-T6 → P3-T7 → P3-T11(M5)
  → P4-T2 → P4-T7(M6)
```

| Critical path node | Why it is on the critical path |
| --- | --- |
| P1-T3 Result decoding | All downstream tasks depend on correct result semantics |
| P1-T7 Temporal splitting | The foundation of the evaluation protocol and of all tasks |
| P2-T3 Rolling protocol | A shared dependency of all metrics and baselines |
| P2-T6 Definition freeze | Without a freeze, baselines cannot converge |
| P3-T2 Paper | The submission window is a hard constraint |
| P4-T2 Definition iteration | The challenge must be based on stable definitions |

> **Any delay on the critical path directly postpones project milestones.**

## 3. Task Dependency Matrix

| Task | Prerequisites | Depended on by |
| --- | --- | --- |
| P1-T1 | — | P1-T2 |
| P1-T2 | P1-T1 | P1-T3, P1-T4 |
| P1-T3 | P1-T2 | P1-T5, P1-T6 |
| P1-T4 | P1-T2 | P1-T6 |
| P1-T5 | P1-T3 | P1-T6 |
| P1-T6 | P1-T4, P1-T5 | P1-T7 |
| P1-T7 | P1-T6 | P1-T8, P2-T3 |
| P1-T8 | P1-T7 | P1-T9, P1-T10 |
| P1-T9 | P1-T8 | P2-T1 |
| P1-T10 | P1-T8 | P3-T7 |
| P1-T11 | P1-T3~T9 | M1 |
| P2-T1 | M1 | P2-T2, P2-T7~T11 |
| P2-T2 | P2-T1 | P2-T3 |
| P2-T3 | P2-T2, P1-T7 | P2-T4, P2-T7~T11 |
| P2-T4 | P2-T3 | P2-T6 |
| P2-T5 | P2-T4 | P2-T6 |
| P2-T6 | P2-T1~T5 | P2-T7~T11 |
| P2-T7~T11 | P2-T6, P2-T3 | P2-T13 |
| P2-T13 | P2-T7~T12 | M3, P3-T3 |
| P3-T2 | M3 | P3-T4, P3-T5 |
| P3-T3 | M3 | P3-T5, P3-T6 |
| P3-T6 | P3-T3 | P3-T7~T9, P3-T11 |
| P3-T7 | P3-T6 | P3-T10, P4-T3 |
| P4-T2 | M5, P4-T1 | P4-T4~T7 |

## 4. External Dependencies

| External dependency | Purpose | Risk | Mitigation |
| --- | --- | --- | --- |
| Official WCA data export | The source of all data | Snapshot changes / restricted access | Pin the snapshot version and keep a local copy |
| Communication with the WCA Results Team | Community adoption | Uncertain responsiveness | Engage early and keep communication courteous |
| HuggingFace Datasets/Models | Hosting data and weights | Platform policy changes | Also provide a mirror/direct link |
| Kaggle | Challenge platform | Rule/resource limits | Fallback: a self-hosted evaluation plus submission entry point |
| NeurIPS submission system | Paper submission | Hard deadline | Freeze material in advance |
| Compute resources (GPU) | Deep learning baselines | Resource scarcity | Set a compute budget; allow degrading |
| W&B / MLflow | Experiment management | Paid quota | Can switch to a local MLflow |

## 5. Parallel and Serial Scheduling

Can be executed in parallel (no mutual dependencies):

- P1-T3 and P1-T4 (decoding / scrambling)
- P2-T7 ~ P2-T11 (the five task implementations, in parallel after P2-T3 completes)
- P3-T7, P3-T8, P3-T9 (release-type tasks, in parallel after P3-T6)
- P4-T4, P4-T5, P4-T6 (method enhancements, in parallel after P4-T2)

Must be serial:

- P1-T3 → P1-T5 → P1-T6 → P1-T7 (the data-semantics dependency chain)
- P2-T1 → P2-T2 → P2-T3 (the framework dependency chain)
- P2-T6 → P2-T7~T11 → P2-T13 (baselines can only converge after the definition freeze)

## 6. Resource Dependencies and Staffing

| Phase | Main roles involved | Person-months (est.) |
| --- | --- | --- |
| Phase 1 | Data engineer ×1.5 + ML engineer ×1 | ~7.5 |
| Phase 2 | ML engineer ×2 + statistics expert ×1 | ~9 |
| Phase 3 | PI ×1 + engineer ×1.5 | ~7.5 |
| Phase 4 | Everyone + community maintainer ×1 | ~9 |

## 7. Further Reading

- [Acceptance Criteria →](/plan/acceptance)
- [Risks and Mitigation →](/plan/risks)
