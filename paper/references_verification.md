# Reference verification record

Online audit of every entry in `references.bib`, performed on 2026-09-21.
Each entry was checked against a publisher, repository or proceedings page.
DOIs were added only when observed on such a page; otherwise a stable URL was
used (the project rule is: never invent a DOI).

**Summary:** 31 entries — 29 verified as existing, 2 newly added
(`cubebench`, `cube_bench_mllm`), 0 deleted, 0 replaced. Bibliographic fields
were completed for all entries (DOI and/or URL, `eprint`/`archivePrefix`, and
`pages`/`booktitle` where applicable).

| key | 标题 | 核验结论 | 证据 URL | 补全的字段 |
| --- | --- | --- | --- | --- |
| `wca_export` | WCA Results Database Export (format v2.0.2) | 存在 | https://www.worldcubeassociation.org/export/results ; https://www.worldcubeassociation.org/api/v0/export/public | 补 `year`、`howpublished`、`note`（快照日期、API 元数据地址） |
| `wca_regs` | WCA Competition Regulations | 存在 | https://www.worldcubeassociation.org/regulations/ | 补 `howpublished`；注明版本日期 2026-04-01 |
| `cubebench` | CubeBench: Diagnosing Interactive, Long-Horizon Spatial Reasoning Under Partial Observations | **新增**（此前为一般性表述，现正式引用真实文献） | https://arxiv.org/abs/2512.23328 ; https://openreview.net/forum?id=MCmQyZ9Gxa ; https://cubebench.c7w.tech/ | 新增条目；补全 12 位作者、`eprint` 2512.23328、`archivePrefix` arXiv、`primaryClass` cs.AI、`note`(ICLR 2026) |
| `cube_bench_mllm` | Cube Bench: A Benchmark for Spatial Visual Reasoning in MLLMs | **新增** | https://arxiv.org/abs/2512.20595 ; https://eehsan.github.io/files/Publications/Dhruv%20Anand.pdf | 新增条目；2 位作者 (Anand, Shareghi)、`eprint` 2512.20595、`primaryClass` cs.CL |
| `deepcubea` | Solving the Rubik's cube with deep reinforcement learning and search | 存在 | https://www.nature.com/articles/s42256-019-0070-z | 补 `doi` 10.1038/s42256-019-0070-z、`url`；核对页码 356–363 |
| `mcaleer_cube` | Solving the Rubik's Cube with Approximate Policy Iteration | 存在 | https://arxiv.org/abs/1805.07470 ; http://deepcube.igb.uci.edu/ | 补 `booktitle`(ICLR 2019)、`note`(arXiv:1805.07470)、`url` |
| `plackett_luce` | The Analysis of Permutations | 存在 | https://www.jstor.org/stable/2346567 ; https://academic.oup.com/jrsssc/article/24/2/193/6953554 | 补 `doi` 10.2307/2346567、`url`；核对卷期页码 24(2):193–202 |
| `bradley_terry` | Rank Analysis of Incomplete Block Designs: I. The Method of Paired Comparisons | 存在 | https://www.jstor.org/stable/2334029 | 补 `url`；核对 Biometrika 39(3/4):324–345 |
| `elo` | The Rating of Chessplayers, Past and Present | 存在 | https://www.nature.com/articles/s41586-023-06124-2 （引用该书） | 保留 `publisher`(Arco, 1978) |
| `glickman_rating` | Parameter Estimation in Large Dynamic Paired Comparison Experiments | 存在；**字段修正** | https://www.glicko.net/research/glicko.pdf ; https://academic.oup.com/jrsssc/article-abstract/48/3/377/6990661 | **移除未核验 DOI**，改 `url`；核对 JRSS-C 48(3):377–394 |
| `nevill_running` | Are there limits to running world records? | 存在 | https://pubmed.ncbi.nlm.nih.gov/16177614/ | 补 `url`；核对 MSSE 37(10):1785–1788 |
| `tatem_sprint` | Athletics: Momentous sprint at the 2156 Olympics? | 存在 | https://www.nature.com/articles/431525a | 补 `doi` 10.1038/431525a、`url`；核对 Nature 431:525 |
| `injury_prediction` | Effective injury forecasting in soccer with GPS training data and machine learning | 存在 | https://doi.org/10.1371/journal.pone.0201264 | 补 `doi`、`url`；核对 PLOS ONE 13(7):e0201264 |
| `m5_competition` | The M5 competition: Background, organization, and implementation | 存在；**字段修正** | https://www.sciencedirect.com/science/article/pii/S0169207021001187 | **移除未核验 DOI**，改 `url`；核对 IJF 38(4):1325–1336 |
| `monash_tsf` | Monash Time Series Forecasting Archive | 存在 | https://arxiv.org/abs/2105.06643 | 补 `booktitle`、`note`、`url` |
| `gluonts` | GluonTS: Probabilistic and Neural Time Series Modeling in Python | 存在 | https://jmlr.org/papers/v21/19-820.html | 补 `url`；核对 JMLR 21(116):1–6 |
| `prequential` | Present Position and Potential Developments: Statistical Theory: The Prequential Approach | 存在 | https://www.jstor.org/stable/2981683 ; https://academic.oup.com/jrsssa/article/147/2/278/7106293 | 补 `doi` 10.2307/2981683、`url`；核对 JRSS-A 147(2):278–292 |
| `hyndman_fpp3` | Forecasting: Principles and Practice (3rd ed.) | 存在 | https://otexts.com/fpp3/ ; https://research.monash.edu/en/publications/forecasting-principles-and-practice-3/ | 补 `edition`、`url`、`publisher` |
| `evt_coles` | An Introduction to Statistical Modeling of Extreme Values | 存在 | https://link.springer.com/book/10.1007/978-1-4471-3675-0 | 补 `doi` 10.1007/978-1-4471-3675-0、`url`、`series` |
| `pickands` | Statistical Inference Using Extreme Order Statistics | 存在 | https://projecteuclid.org/journals/annals-of-statistics/volume-3/issue-1/Statistical-Inference-Using-Extreme-Order-Statistics/10.1214/aos/1176343003.full | 补 `doi` 10.1214/aos/1176343003、`url` |
| `bayesian_hierarchical` | Bayesian Data Analysis (3rd ed.) | 存在 | https://baike.baidu.com/item/Bayesian%20Data%20Analysis%2C%20Third%20Edition/56295776 | 补 `isbn` 9781439840955；校对 6 位作者 |
| `did` | Minimum Wages and Employment: A Case Study of the Fast-Food Industry in New Jersey and Pennsylvania | 存在 | https://www.jstor.org/stable/2118030 ; https://davidcard.berkeley.edu/papers/njmin-aer.pdf | 补 `url`；核对 AER 84(4):772–793 |
| `iv` | Identification of Causal Effects Using Instrumental Variables | 存在 | https://www.jstor.org/stable/2291629 | 补 `url`；保留 `doi` 10.1080/01621459.1996.10476902，核对 JASA 91(434):444–455 |
| `causal_forest` | Estimation and Inference of Heterogeneous Treatment Effects using Random Forests | 存在 | https://www.tandfonline.com/doi/full/10.1080/01621459.2017.1319839 | 补 `url`；核对 JASA 113(523):1228–1242 |
| `sensitivity_analysis` | The Central Role of the Propensity Score in Observational Studies for Causal Effects | 存在 | https://academic.oup.com/biomet/article/70/1/41/240879 | 补 `doi` 10.1093/biomet/70.1.41、`url`；核对 Biometrika 70(1):41–55 |
| `datasheets` | Datasheets for Datasets | 存在 | https://dl.acm.org/doi/10.1145/3458723 | 补 `doi`、`url`；核对 CACM 64(12):86–92 |
| `model_cards` | Model Cards for Model Reporting | 存在 | https://dl.acm.org/doi/10.1145/3287560.3287596 | 补 `doi`、`url`；补全 9 位作者、`pages` 220–229 |
| `neurips_dnb` | Proceedings of the NeurIPS Datasets and Benchmarks Track | 存在 | https://datasets-benchmarks-proceedings.neurips.cc/ | 补 `howpublished`、`url`、`note` |
| `leakage_kaufman` | Leakage in Data Mining: Formulation, Detection, and Avoidance | 存在 | https://dl.acm.org/doi/10.1145/2382577.2382579 | 补 `doi`、`url`；核对 TKDD 6(4):15:1–15:21 |
| `sculley_rigor` | Winner's Curse? On Pace, Progress, and Empirical Rigor | 存在 | https://openreview.net/forum?id=rJWF0Fywf | 补 `url`；核对 ICLR 2018 Workshop |
| `breiman_cultures` | Statistical Modeling: The Two Cultures | 存在 | https://projecteuclid.org/journals/statistical-science/volume-16/issue-3/Statistical-Modeling--The-Two-Cultures-with-comments-and-a/10.1214/ss/1009213726.full | 补 `doi` 10.1214/ss/1009213726、`url`；核对 Statistical Science 16(3):199–231 |

## Notes

1. **CubeBench family (two verified papers).** An earlier draft avoided naming a
   specific CubeBench paper because it could not then be verified. Two fresh
   searches confirmed the family is real, and both are now cited:
   * Gao et al., *CubeBench: Diagnosing Interactive, Long-Horizon Spatial
     Reasoning Under Partial Observations*, ICLR 2026 (arXiv:2512.23328;
     OpenReview `MCmQyZ9Gxa`; project page https://cubebench.c7w.tech/); and
   * Anand & Shareghi, *Cube Bench: A Benchmark for Spatial Visual Reasoning in
     MLLMs*, 2025 (arXiv:2512.20595).
   Related Work now states the positioning explicitly: these benchmarks evaluate
   LLM/MLLM agents' spatial reasoning and planning on *synthetic* cube states,
   whereas WCA-Bench evaluates prediction and inference on *real, noisy,
   rule-governed competition records*; the two are complementary, not
   competing.
2. **DOIs not independently resolved were removed rather than guessed.** For
   `glickman_rating` and `m5_competition` the previously assumed DOI could not be
   confirmed on a publisher page, so it was replaced by a stable URL. All
   remaining DOIs were observed on a publisher or repository page.
3. **A `%`-comment in `references.bib` must not contain `@`.** BibTeX does not
   treat `%` as a comment character outside entries, so a comment mentioning
   `@misc`/`@book` was parsed as a broken entry. The comment text was reworded;
   `main.blg` now reports zero errors.
4. Two web-only sources (`wca_export`, `wca_regs`, `neurips_dnb`) have no DOI by
   nature and use `howpublished` + `url`, consistent with the project rule.

## Re-validation

After the update:

* `python check_bib.py` → 30 unique citation keys, all defined, none unused,
  all `\input` targets exist, all environments balanced.
* `latexmk -xelatex main.tex` → 29 pages, `main.log` reports **0 undefined
  citations / references**, `main.blg` reports **0 errors**.
