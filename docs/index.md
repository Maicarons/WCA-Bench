---
layout: home

hero:
  name: WCA-Bench
  text: A Standardized Benchmark for Sports Data Analysis
  tagline: The first comprehensive machine learning benchmark built on the complete public competition data of the World Cube Association (WCA) — 5 core tasks, 289k competitors, 6.6M results, and a strict leakage-free evaluation protocol
  actions:
    - theme: brand
      text: Read the Project Proposal
      link: /guide/
    - theme: alt
      text: View the Development Plan
      link: /plan/
    - theme: alt
      text: View on GitHub
      link: https://github.com/

features:
  - icon: 🎯
    title: Define a Scientific Question
    details: Rather than chasing a new model, we ask "under the real constraints of competitive sports data, how do different methodologies perform?" The question itself carries independent research value.
  - icon: 🗄️
    title: Real, Not Synthetic
    details: Data comes from the official WCA database export (persons / results / scrambles, etc.), covering 17 active events and 23 years of longitudinal records.
  - icon: 🧩
    title: A Spectrum of Five Tasks
    details: Result prediction (regression), placement prediction (ranking), DNF prediction (classification), human limit estimation (extremes), and skill transfer (causal inference).
  - icon: 🔒
    title: Strictly Leakage-Free
    details: Temporal splitting plus rolling-window evaluation; benchmark statistics are frozen during the test window, eliminating every form of future information leakage.
  - icon: 📊
    title: A Stratified Evaluation Framework
    details: Results are reported along four dimensions — event, competitor skill level, time, and region — so that no dominant group masks the rest.
  - icon: 🔁
    title: Reproducibility First
    details: Training code, random seeds, preprocessing scripts, model weights (HuggingFace), and compute cost are all released.
---

## What Is This

WCA-Bench is the **first comprehensive machine learning benchmark built on the complete public competition data of the World Cube Association (WCA)**. It covers five core tasks — result prediction, placement prediction, DNF prediction, human limit estimation, and skill transfer analysis — and provides a standardized evaluation protocol and a reproducible experimental framework for the field of sports data analysis.

## Documentation Map

| Section | Contents | Entry |
| --- | --- | --- |
| **Project Proposal** | Objectives, scope, technical approach overview, expected outcomes | [Enter →](/guide/) |
| **Technical Design** | Data infrastructure, task suite definitions, evaluation framework | [Enter →](/data/) |
| **Development Plan** | Directory organization, phase breakdown, milestones, task breakdown, dependencies and acceptance criteria | [Enter →](/plan/) |

## Quick Start (Documentation Site)

```bash
npm install          # install dependencies
npm run docs:dev     # local preview (default http://localhost:5173)
npm run docs:build   # build the static site to docs/.vitepress/dist
npm run docs:preview # preview the build output
```
