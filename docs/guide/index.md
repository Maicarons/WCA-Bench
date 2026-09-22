# Project Proposal: Executive Summary

> This document is the entry point of the overall WCA-Bench project proposal, intended for review and go/no-go decisions. Full technical details and the development schedule are covered in the "Technical Design" and "Development Plan" sections.

## One-Sentence Description

**WCA-Bench is the first comprehensive machine learning benchmark built on the complete public competition data of the World Cube Association (WCA)**, covering five core tasks — result prediction, placement prediction, DNF prediction, human limit estimation, and skill transfer analysis — and providing a standardized evaluation protocol and a reproducible experimental framework for sports data analysis.

## Proposal Structure

| Chapter | Core Question | Link |
| --- | --- | --- |
| Project Overview and Objectives | Why do this? What problem does it solve? | [View](/guide/overview) |
| Project Scope | What is in scope, and what is out of scope? | [View](/guide/scope) |
| Technical Approach Overview | How is it implemented? What is the stack and architecture? | [View](/guide/architecture) |
| Expected Outcomes and Success Criteria | What are the deliverables? What counts as success? | [View](/guide/outcomes) |

## Key Conclusions

1. **The problem is real.** Sports data analysis lacks a comprehensive benchmark grounded in real competition data, with explicit domain constraints and support for standardized evaluation.
2. **The data foundation is ready.** The official public WCA database export (289k competitors, 6.6M results, 17 active events) can be obtained directly, with no need to build a data collection pipeline.
3. **The technology stack is mature.** Polars / PyArrow for large-scale data processing, PyTorch for training, PyMC/NumPyro for Bayesian inference, and HuggingFace for hosting data and weights.
4. **The main risk is community adoption.** This can be mitigated through early collaboration with the WCA Results Team and the speedcubing community.

## Relationship to Cube-Solving Benchmarks

WCA-Bench is **complementary** to, rather than competitive with, the CubeBench family: the latter evaluates an LLM's spatial reasoning and sequence planning abilities (solving the cube), whereas WCA-Bench evaluates an AI system's **prediction and inference** abilities on real competitive data. Together they form a complete picture of research on "cubes and AI".

## Quick Navigation

- [→ Project Overview and Objectives](/guide/overview)
- [→ Task Suite Overview](/tasks/)
- [→ Development Plan Overview](/plan/)
- [→ Milestones and Phase Breakdown](/plan/roadmap)
