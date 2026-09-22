# Phase Breakdown and Milestones

## 1. Overall Roadmap

| Phase | Time | Theme | Core objective | Exit milestone |
| --- | --- | --- | --- | --- |
| Phase 1 | Months 1–3 | Data infrastructure | Reproducible data production | **M1** Data pipeline complete |
| Phase 2 | Months 4–6 | Task definitions and baseline implementation | Five tasks evaluable with baselines | **M2 / M3** Baselines complete |
| Phase 3 | Months 7–9 | Benchmark release and community building | Paper submission + public release | **M4 / M5** Submission and release |
| Phase 4 | Months 10–12 | Iteration and expansion | Community feedback loop + challenge | **M6** Challenge |

```text
Month  1   2   3   4   5   6   7   8   9   10  11  12
      ├───────────┤
      Phase 1 Data infrastructure
                  ├───────────┤
                  Phase 2 Task definition and baselines
                              ├───────────┤
                              Phase 3 Benchmark release
                                          ├───────────┤
                                          Phase 4 Iteration and expansion
Milestones M1      M2  M3          M4  M5              M6
```

## 2. Key Milestones

| Milestone | Time | Name | Deliverables | Acceptance highlights |
| --- | --- | --- | --- | --- |
| **M1** | Month 3 | Data pipeline complete | Preprocessed data, loader, data card | Reproducible with a single command; all quality checks pass |
| **M2** | Month 5 | Task definitions frozen | Five task definition documents, evaluation protocol | All five elements present; review passed |
| **M3** | Month 6 | Baseline experiments complete | Baseline results and leaderboard for five tasks | All baselines runnable; complete Report structure |
| **M4** | Month 7 | NeurIPS submission | Paper draft + code + data | Submission material complete before the abstract deadline |
| **M5** | Month 9 | Public release | GitHub repository + HuggingFace dataset | Repository public, dataset downloadable, CI green |
| **M6** | Month 12 | Community challenge | Kaggle competition + results analysis | Competition live, teams participating, analysis report produced |

## 3. Detailed Milestone Definitions

### M1 · Data Pipeline Complete (Month 3)

- **Prerequisites**: WCA export obtained, development environment ready
- **Deliverables**:
  - Full `data/processed/*.parquet` artifacts
  - The complete `src/wca_bench/data/` module (loader / decoders / features / splits)
  - The `datacard.md` data card
  - `scripts/build_dataset.py` one-command build
- **Acceptance criteria**: see [Acceptance Criteria · A1](/plan/acceptance#a1-data-pipeline)

### M2 · Task Definition Frozen (Month 5)

- **Prerequisites**: M1 complete
- **Deliverables**: five task definitions (inputs/outputs/metrics/baselines/challenges), evaluation protocol implementation, hard sample subset definitions
- **Acceptance criteria**: see [Acceptance Criteria · A2](/plan/acceptance#a2-task-definition)

### M3 · Baseline Experiments Complete (Month 6)

- **Prerequisites**: M2 complete
- **Deliverables**:
  - ≥ 3–4 baselines per task (≥ 18 in total)
  - An initial leaderboard
  - Experiment configurations and archived results
- **Acceptance criteria**: see [Acceptance Criteria · A3](/plan/acceptance#a3-baseline-implementation)

### M4 · NeurIPS Submission (Month 7)

- **Prerequisites**: M3 complete
- **Deliverables**: paper draft, appendix, reproducibility package
- **Risk**: the submission window is a hard constraint and must be aligned in advance

### M5 · Public Release (Month 9)

- **Prerequisites**: M4 complete
- **Deliverables**:
  - Public GitHub repository (Apache-2.0)
  - HuggingFace dataset and model weights
  - Documentation site online
- **Acceptance criteria**: see [Acceptance Criteria · A4](/plan/acceptance#a4-release)

### M6 · Community Challenge (Month 12)

- **Prerequisites**: M5 complete + community feedback collected
- **Deliverables**: Kaggle competition, results analysis report, journal extension plan

## 4. Phase Exit Criteria

Every phase must end with:

- [ ] All tasks of the phase in "done" state
- [ ] Deliverables archived and passed acceptance
- [ ] Documentation updated
- [ ] CI fully green
- [ ] Milestone review passed

## 5. Time Buffers and Adjustments

| Phase | Planned duration | Buffer | Notes |
| --- | --- | --- | --- |
| Phase 1 | 3 months | 2 weeks | Data decoding and quality checks are the high-risk points |
| Phase 2 | 3 months | 2 weeks | Sequence models and GNN training may overrun |
| Phase 3 | 3 months | 1 week | The submission window is fixed, so the buffer is limited |
| Phase 4 | 3 months | 3 weeks | Depends on community feedback; high uncertainty |

## 6. Further Reading

- [Phase 1: Data Infrastructure →](/plan/phase-1)
- [Phase 2: Task Definition and Baselines →](/plan/phase-2)
- [Phase 3: Benchmark Release →](/plan/phase-3)
- [Phase 4: Iteration and Expansion →](/plan/phase-4)
- [Dependencies →](/plan/dependencies)
