# Risks and Mitigation

## 1. Risk Register

| ID | Risk | Category | Probability | Impact | Level |
| --- | --- | --- | --- | --- | --- |
| R1 | WCA data updates mean the test set is no longer "the future" | Data | High | Medium | **High** |
| R2 | Benchmark saturation (a task rapidly reaches high accuracy) | Scientific | Medium | High | **High** |
| R3 | The community does not adopt it, limiting impact | Community | Medium | High | **High** |
| R4 | Ethical and privacy disputes | Ethics | Low | High | **Medium** |
| R5 | Multi-blind decoding / rule handling errors | Technical | Medium | High | **High** |
| R6 | Deep learning baseline training overruns | Technical | Medium | Medium | **Medium** |
| R7 | Missing the submission window | Schedule | Medium | High | **High** |
| R8 | Insufficient reproducibility casting doubt during review | Scientific | Medium | High | **High** |

## 2. Detailed Mitigation Strategies

### R1 · Data Risk

**Risk**: Updates to WCA data may mean the benchmark's test set is no longer "the future". Because the WCA database keeps being updated, competition data from 2026 onward is continuously added.

**Mitigation**:

- Fix the test set to **2025–2026**
- Release subsequently added data as an "**Extended Test Set**"
- **The main leaderboard is always based on the fixed test window**
- This follows the convention of time-series benchmarks and preserves historical comparability

### R2 · Benchmark Saturation Risk

**Risk**: If the baseline methods for a task rapidly reach very high accuracy (for example, AUC > 0.95 for DNF prediction), the benchmark may lose its discriminative power.

**Mitigation**:

- Design each task to have a sufficient "**hard sample**" subset
  - For example, DNF prediction additionally reports performance on the "high-uncertainty" subset (competitor historical DNF rate between 0.1 and 0.3)
- The five tasks cover a **continuous difficulty spectrum** from easy to hard
- Introduce a cost dimension: report performance together with compute, so that "compute for accuracy" cannot hide a loss of discriminative power

### R3 · Community Adoption Risk

**Risk**: The value of a benchmark depends on whether the community uses it. If the WCA community or the ML community does not adopt it, the project's impact will be limited.

**Mitigation**:

- Establish relationships with the **WCA Results Team** and the **speedcubing community** from the very start of the project
- Position WCA-Bench as a tool that "**serves the community**":
  - Competitors can use it to analyze their own performance
  - Competition organizers can use it to optimize round settings and advancement rules
- Lower the barrier to entry: provide a starter kit, submission template, and evaluation scripts

### R4 · Ethical and Privacy Risk

**Risk**: Although WCA data is public, competitors' participation records could be used for inappropriate purposes (such as gambling prediction or competitor discrimination).

**Mitigation**:

- State the permitted and prohibited use cases **explicitly in the data card**
- Provide an **anonymization option** — allowing competitors to request removal of their personal records from the benchmark data (retaining aggregate statistics but not individual-level data)
- Comply with the acceptable use terms for WCA data
- Explicitly prohibit gambling-related uses in the challenge rules

### R5 · Technical Risk: Rule Decoding Errors

**Risk**: Errors in multi-blind encoding, special values (-1/-2), or the round trimming mechanism will systematically contaminate all downstream tasks.

**Mitigation**:

- **Round-trip tests** for multi-blind decoding (`encode(decode(v)) == v`)
- Consistency checks between reconstructed average and the official value, with warnings below the threshold
- Manual sampling checks on boundary samples
- The data quality checklist serves as a Phase 1 gate

### R6 · Technical Risk: Training Overruns

**Risk**: Training sequence models (LSTM/Transformer) and graph neural networks may exceed the compute budget and the schedule.

**Mitigation**:

- Start early and set an upper bound on the compute budget
- Allow degrading to a smaller model / subsampled training
- Ship non-GNN / non-deep baselines first, with deep baselines added incrementally
- Report on two dimensions, "performance–cost", to avoid a pure-accuracy orientation

### R7 · Schedule Risk: Submission Window

**Risk**: The NeurIPS submission deadline is a hard constraint.

**Mitigation**:

- Freeze all material one week in advance
- Set buffers on M2/M3 (2 weeks each)
- Advance paper writing and engineering in parallel

### R8 · Scientific Risk: Reproducibility

**Risk**: Reviewers or third parties cannot reproduce the results, affecting acceptance and community trust.

**Mitigation**:

- An independent third party reproduces and validates the results (P3-T3)
- Environment lock, fixed seeds, downloadable raw predictions
- Clear reproduction levels (L1/L2/L3) and minimum requirements

## 3. Risk Monitoring Mechanisms

| Mechanism | Frequency | Owner |
| --- | --- | --- |
| Risk register update | Biweekly | PI |
| Milestone review | Every milestone | Everyone |
| CI gate | Every commit | Automated |
| Community feedback triage | Biweekly in Phase 4 | Community maintainer |

## 4. Escalation Path

```text
Risk triggered
   │
   ├─ Low impact ──► Log in the register, routine mitigation
   │
   ├─ Medium impact ──► Assess within two weeks, adjust task priorities
   │
   └─ High impact ──► Convene a review meeting immediately, adjust milestones if necessary
```

## 5. Further Reading

- [Publication Strategy →](/plan/publication)
- [Acceptance Criteria →](/plan/acceptance)
