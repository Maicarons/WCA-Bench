# WCA-Bench paper

LaTeX sources for *WCA-Bench: A Standardized Benchmark for Sports Analytics on
World Cube Association Competition Data*, in **two fully compiled versions**:

| Version | Root file | Language | Class / engine |
| --- | --- | --- | --- |
| **English (primary)** | `main.tex` | English | `article` + **XeLaTeX** |
| **Chinese** | `zh/main.tex` | 中文 | `ctexart` + **XeLaTeX** |

Both versions share a single bibliography (`references.bib`) and the same real
numbers, figures and structure. The Chinese version uses `ctex` (`ctexart`)
and keeps proper nouns (WCA-Bench, Plackett–Luce, XGBoost, GNN, DNF,
Psych Sheet, …) in English.

## Directory layout

```
paper/
├── main.tex              # English root (primary version)
├── preamble.tex          # English packages and macros
├── references.bib        # shared bibliography (30 entries)
├── check_bib.py          # static checker for BOTH language versions
├── Makefile              # make en / zh / all / figures / check / arxiv
├── .latexmkrc            # forces xelatex + bibtex (English)
├── references_verification.md   # online audit of every bibliography entry
├── data_verification.md         # snapshot vs. official WCA export figures
├── figures/
│   ├── make_figures.py   # generates figures from examples/leaderboard.csv
│   └── *.pdf             # shared by both language versions
├── sections/             # English sections (00_abstract … 10_appendix)
└── zh/
    ├── main.tex          # Chinese root
    ├── preamble.tex      # Chinese packages/macros (ctex)
    ├── .latexmkrc        # forces xelatex + bibtex (Chinese)
    └── sections/         # Chinese sections (00_abstract … 10_appendix)
```

## Prerequisites

* **XeLaTeX + BibTeX** (TeX Live 2021+ or MiKTeX). Tested with TeX Live 2024.
* **Chinese support** for the Chinese version:
  * TeX Live: install the `ctex` + `xeCJK` packages, usually via
    `tlmgr install ctex xecjk` (or the distro package `texlive-lang-chinese`
    / `texlive-lang-cjk` on Debian/Ubuntu).
  * Fonts: on Windows, `ctex` uses the built-in SimSun and needs no extra
    install. On Linux install e.g. `fonts-noto-cjk`
    (`apt-get install fonts-noto-cjk`) or `fonts-arphic-uming`; on macOS the
    system Songti/Song faces are picked up automatically. If `ctex` cannot find
    a CJK font, pass a fontset explicitly, e.g.
    `\documentclass[11pt,fontset=fandol]{ctexart}` (Fandol fonts ship with
    TeX Live and need no system fonts).
* **Python 3.9+** with `matplotlib`, `pandas`, `numpy` (figures and the checker).

TeX Live packages used (all standard): `geometry`, `newtxtext`, `newtxmath`
(English only), `ctex`/`xeCJK` (Chinese only), `amsmath`, `amssymb`,
`mathtools`, `booktabs`, `multirow`, `array`, `tabularx`, `threeparttable`,
`makecell`, `graphicx`, `xcolor`, `caption`, `subcaption`, `algorithm`,
`algpseudocode`, `microtype`, `enumitem`, `url`, `natbib`, `hyperref`.

## Building

```bash
# both versions (figures are regenerated first)
make            # or: make all

# English only  -> main.pdf
make en

# Chinese only  -> zh/main.pdf
make zh

# manual, from the relevant directory
latexmk -xelatex main.tex          # English
(cd zh && latexmk -xelatex main.tex)   # Chinese
```

`latexmk` runs XeLaTeX, BibTeX and the extra passes needed to resolve
references automatically.

## Regenerating the figures

The four PDF figures are generated **from the real baseline results** in
`../examples/leaderboard.csv`; nothing is hard-coded and the script performs no
network access. Both language versions include the same figures.

```bash
python figures/make_figures.py
```

| File | Content |
| --- | --- |
| `fig1_task_overview.pdf` | four-panel overview of T1/T2/T3/T5 baselines |
| `fig2_result_prediction.pdf` | T1 `MAE(log)` per model |
| `fig3_dnf_models.pdf` | T3 AUC-PR per model |
| `fig4_transfer_pairs.pdf` | T5 number of identifiable event pairs |

If the CSV is missing, the script prints a clear error and exits with status 1.

## Checking consistency without TeX

`check_bib.py` verifies **both** `main.tex` and `zh/main.tex`:

1. every `\input{...}` target exists;
2. every `\cite`-family key is defined in the shared `references.bib` (unused
   entries are listed as warnings);
3. `\begin{...}` / `\end{...}` are balanced in every source file.

```bash
python check_bib.py          # verbose
python check_bib.py --quiet  # print problems only
```

Alternatively, after a build, search each log for undefined citations:

```bash
grep -i "undefined" main.log
grep -i "undefined" zh/main.log
```

## Bibliography and data verification

* `references_verification.md` — an online audit of all 30 bibliography
  entries (existence, DOI/URL completion, the CubeBench check, removals).
* `data_verification.md` — the repo snapshot counts versus the official WCA
  export pages (which publish no row counts), including export date and format
  version.

## Exporting arXiv submission packages

```bash
make arxiv      # English: main.tex, preamble.tex, references.bib, sections/, figures/
make arxiv-zh   # Chinese: bundles references.bib and rewrites the \bibliography path
```

Each target produces a `*.tar.gz` containing sources (not the compiled PDF as
the only artifact). Upload it and select `main.tex` as the root file in the
arXiv submission interface.

## Notes on the numbers

All quantitative claims in `sections/06_baselines_results.tex` (and the Chinese
counterpart) are taken from `../examples/leaderboard.md` / `leaderboard.csv`
and the per-model JSON reports in `../examples/`. They correspond to a sampled,
single-machine ("small mode") run over **21 baselines** and are reproducible
with the commands documented in the main repository README. The dataset scale
figures are the exact row counts of the pinned export snapshot (v2.0.2,
2026-09-21); see `data_verification.md`.
