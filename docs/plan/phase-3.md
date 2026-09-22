# Phase 3: Benchmark Release and Community Building (Months 7–9)

> **Objective**: Complete the paper submission, publicly release the code, data, and leaderboard, and start community building.
> **Exit milestones**: [M4 NeurIPS Submission](/plan/roadmap#m4-·-neurips-submission-month-7), [M5 Public Release](/plan/roadmap#m5-·-public-release-month-9)

## 1. Phase Objectives

- Publish the data on HuggingFace Datasets
- Release the code repository on GitHub (Apache-2.0 License)
- Submit to the NeurIPS Evaluations & Datasets Track
- Promote the benchmark in the WCA community and the sports data analysis community

## 2. Work Breakdown (WBS)

| Task ID | Task name | Weeks | Prerequisites | Deliverables |
| --- | --- | --- | --- | --- |
| P3-T1 | Paper framework and figures | W25–W26 | M3 | Paper outline, results figures |
| P3-T2 | Paper draft writing | W25–W28 | P3-T1 | Full paper draft |
| P3-T3 | Reproducibility package | W26–W27 | M3 | Complete `submission/` package |
| P3-T4 | Internal review and revision | W27–W28 | P3-T2 | Review comments and revised draft |
| P3-T5 | NeurIPS submission (M4) | W28 | P3-T2, P3-T3 | Submission confirmation |
| P3-T6 | GitHub repository made public | W29–W30 | P3-T3 | Public repository (Apache-2.0) |
| P3-T7 | HuggingFace dataset release | W29–W31 | P3-T6 | Dataset + data card page |
| P3-T8 | Model weight hosting | W30–W31 | P3-T6 | HuggingFace Models |
| P3-T9 | Documentation site online | W30–W32 | P3-T6 | Online documentation (VitePress) |
| P3-T10 | Submission specification and evaluation service | W31–W33 | P3-T7 | Submission template + validation scripts |
| P3-T11 | Community outreach kickoff (M5) | W32–W36 | P3-T6 | WCA forum/community posts, channel liaison |
| P3-T12 | Post-release monitoring and response | W34–W36 | P3-T11 | Issue responses, FAQ |

> Weeks continue from Phase 2 (W25 = the project's 25th week); the phase lasts 12 weeks (W25–W36).

## 3. Detailed Task Descriptions

### P3-T1 · Paper Framework and Figures

- Organize according to the NeurIPS E&D Track structure: Motivation / Dataset / Tasks / Protocol / Baselines / Results / Limitations
- Produce the core figures: data distributions, task illustrations, baseline comparisons, stratified heatmaps
- **Acceptance**: figures can be embedded directly into the paper (vector format)

### P3-T2 · Paper Draft Writing

- Core contribution claims:
 1. The first standardized benchmark for sports data analysis built on real WCA competition data
 2. Five evaluation tasks defined with domain-specific challenges
 3. A strict leakage-free evaluation protocol and a stratified evaluation framework
 4. Complete baseline implementations and reproducible experimental code
- Write the Limitations and ethics sections explicitly
- **Acceptance**: a complete draft that is internally readable

### P3-T3 · Reproducibility Package

- Package according to the [leaderboard submission format](/evaluation/reproducibility#_7-leaderboard-submission-format)
- Environment lock, seeds, and compute report all complete
- **Acceptance**: a third party can reproduce the main results from the material (L3)

### P3-T5 · NeurIPS Submission (M4)

- Strictly observe the abstract and full-text deadlines
- Freeze all material one week in advance
- **Acceptance**: submission confirmation received

### P3-T6 · GitHub Repository Made Public

- Add `README.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `LICENSE`, `CITATION.cff`
- Clean up sensitive/temporary files and confirm `.gitignore` is correct
- Enable Issues and Discussions
- **Acceptance**: the repository is public, CI is green, and the README guides new users to a successful run

### P3-T7 · HuggingFace Dataset Release

- Upload the preprocessed artifacts and split indices
- Write the dataset card (reusing `datacard.md`, including permitted/prohibited uses)
- **Acceptance**: loadable via `datasets.load_dataset`

### P3-T8 · Model Weight Hosting

- Upload each baseline model's weights to HuggingFace Models
- Attach the training configuration and compute report
- **Acceptance**: weights are downloadable and reproduce the metrics

### P3-T9 · Documentation Site Online

- Build and deploy the VitePress site (GitHub Pages / self-hosted)
- Keep content in sync with the code version
- **Acceptance**: the site is publicly accessible with complete navigation

### P3-T10 · Submission Specification and Evaluation Service

- Provide the submission template, validation scripts, and leaderboard submission entry point
- State the inclusion criteria clearly (reproduction level ≥ L3)
- **Acceptance**: the submission validation script can automatically check the completeness of the material

### P3-T11 · Community Outreach Kickoff (M5)

- Engage with the WCA Results Team and establish a formal communication channel
- Post on the SpeedSolving forum, Reddit r/Cubers, and ML communities
- Position it as a tool that "serves the community" (competitors analyzing their performance, organizers optimizing rounds)
- **Acceptance**: at least 2 effective community channels established and feedback received

## 4. Phase Deliverables

| ID | Deliverable | Corresponding tasks |
| --- | --- | --- |
| D1 | WCA-Bench dataset (HuggingFace) | P3-T7 |
| D7 | Main paper (NeurIPS E&D) | P3-T2, P3-T5 |
| D8 | Public code repository | P3-T6 |
| — | Submission specification and evaluation scripts | P3-T10 |
| — | Online documentation site | P3-T9 |

## 5. Phase Acceptance Criteria

- [ ] The paper is submitted before the deadline (M4)
- [ ] The repository is public and contains the complete governance files (LICENSE / CONTRIBUTING / CODE_OF_CONDUCT / CITATION)
- [ ] The dataset can be loaded directly from HuggingFace, with a complete card
- [ ] Model weights are downloadable and reproduce the metrics (within tolerance)
- [ ] The documentation site is publicly accessible with complete navigation
- [ ] The submission validation script can automatically check submission material
- [ ] At least 2 effective community channels established (M5)

## 6. Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Hard submission deadline | Missing the window | Freeze material one week early and reserve buffer |
| Reproducibility problems exposed during review | Affects acceptance | An independent third party reproduces the results in P3-T3 |
| Disputes over the data release license | Release blocked | Confirm the WCA data use terms in advance |
| Lukewarm community response | Limited impact | Engage the WCA Results Team in advance |

## 7. Further Reading

- [Phase 4: Iteration and Expansion →](/plan/phase-4)
- [Publication Strategy →](/plan/publication)
