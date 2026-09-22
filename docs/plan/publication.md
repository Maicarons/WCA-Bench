# Publication Strategy

## 1. First Paper Target

**NeurIPS 2026 Evaluations & Datasets Track.**

The NeurIPS E&D Track explicitly welcomes:

- Submissions that "introduce datasets with a clear explanation of their scope, assumptions, limitations, and how they support or shape evaluation claims in the AI/ML lifecycle"
- "Benchmarking, benchmarking tools, and methodologies on new or existing datasets"

WCA-Bench **fits this scope perfectly**.

## 2. Core Contribution Claims

1. The **first standardized benchmark for sports data analysis built on real WCA competition data**
2. **Five evaluation tasks with domain-specific challenges**
3. A **strict leakage-free evaluation protocol and a stratified evaluation framework**
4. **Complete baseline implementations and reproducible experimental code**

## 3. Suggested Paper Structure

| Section | Key points |
| --- | --- |
| Introduction | Problem statement: fragmented research and the lack of standardization |
| Related Work | The CubeBench family, sports data analysis, time-series benchmarks |
| The WCA-Bench Dataset | Data sources, scale, rule decoding, splits, data card summary |
| Tasks | Five task definitions, metrics, domain challenges |
| Evaluation Protocol | Rolling window, frozen statistics, four-way stratification, statistical testing |
| Baselines & Results | ≥ 18 baselines, leaderboard, stratified results |
| Discussion | Methodological insights, performance–cost trade-offs, saturation analysis |
| Limitations | Extrapolation risk, data bias, regional imbalance |
| Ethics & Broader Impact | Permitted/prohibited uses, privacy considerations |

## 4. Future Publication Roadmap

### Second Paper (Applied)

- **Content**: systematically evaluate the performance gap between classical statistical methods and deep learning methods on WCA-Bench
- **Target journals**: *Journal of Quantitative Analysis in Sports* or *Machine Learning*

### Third Paper (Methodological)

- **Content**: propose new causal inference methods addressing the challenges of the skill transfer task in WCA-Bench
- **Target venues**: KDD or ICDM

### Fourth Paper (Survey)

- **Content**: based on the experimental results of WCA-Bench, write a survey of "rule-constrained prediction" in sports data analysis
- **Target journal**: *ACM Computing Surveys*

## 5. Publication and Release Timeline

```text
Month 7   NeurIPS submission (M4)
   │
Month 9   Public release (M5): GitHub + HuggingFace + documentation site
   │
Months 10-12  Challenge + journal extension planning (M6)
   │
Next year  Second paper (applied) → third paper (method) → fourth paper (survey)
```

## 6. Academic Integrity and Compliance

| Item | Convention |
| --- | --- |
| Data license | Comply with the WCA public data use terms |
| Ethics statement | The paper includes Ethics / Broader Impact sections |
| Reproducibility material | Submit reproducibility material alongside the paper (appendix + anonymized repository) |
| Double-blind requirements | Handle anonymized repository links according to conference rules |
| Contribution statement | Use the CRediT contributor role taxonomy |

## 7. Authorship and Contributions

We recommend using **CRediT** to make contributions explicit:

| Role | Description |
| --- | --- |
| Conceptualization | Project positioning and task design |
| Data Curation | Data acquisition, decoding, and splitting |
| Methodology | Evaluation protocol and statistical methods |
| Software | Pipeline, baselines, and leaderboard implementation |
| Writing – Original Draft | Lead writing of the paper |
| Writing – Review & Editing | All authors |

## 8. Further Reading

- [Milestones · M4 / M5 →](/plan/roadmap#_2-key-milestones)
- [Reproducibility Requirements →](/evaluation/reproducibility)
