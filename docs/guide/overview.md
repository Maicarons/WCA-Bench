# Project Overview and Objectives

## 1. Background and Motivation

WCA data analysis currently suffers from three prominent problems:

### 1.1 Fragmented Research

Existing machine learning work on WCA data is scattered across single tasks:

- Using kernel density estimation to predict competition placement
- Using linear regression to predict world records
- Using Gaussian processes and extreme value theory to estimate human limits

Each of these works uses **different data splitting schemes, evaluation metrics, and preprocessing pipelines**, which makes their results mutually incomparable.

### 1.2 Lack of Standardized Evaluation

The existing "CubeBench" family of benchmarks focuses on **cube solving** — evaluating an LLM's spatial reasoning and sequence planning ability, and diagnosing cognitive bottlenecks by having models call tools to solve the cube. These benchmarks:

- Are **unrelated** to real WCA competition data
- Cannot answer questions such as "which model predicts competitor results more accurately" or "which method estimates DNF probability better"

### 1.3 Domain-Specific Challenges Are Overlooked

WCA data has distinctive structural characteristics that require models to explicitly model rule constraints, something generic time-series forecasting models are usually unable to handle directly:

| Characteristic | Description |
| --- | --- |
| Longitudinal records | A competitor's career spans many competitions and several years |
| Cross-event skill transfer | Quantifiable transfer effects exist among the 17 events |
| Round formats | Formats such as average of 5 and mean of 3 affect how results are computed |
| Special encodings | DNF = `-1`, DNS = `-2`, multi-blind `1SSAATTTTT` / `0DDTTTTTMM` |
| Trimming mechanism | ao5 discards the best and worst attempt, which amplifies the impact of a single DNF |

## 2. Project Objectives

### 2.1 Overall Objective

> **Define an evaluation science question**: under the real constraints of competitive sports data, how do different methodologies (classical statistics, deep learning, graph learning, generative models) perform?

The goal of WCA-Bench is **not to propose a new prediction model**, but to provide standardized evaluation infrastructure. This question carries independent research value.

### 2.2 Specific Objectives

| ID | Objective | How it is measured |
| --- | --- | --- |
| G1 | Build reproducible data infrastructure | The preprocessing pipeline runs with a single command and emits Parquet plus a data card |
| G2 | Formally define five task classes | Every task has explicit inputs/outputs/metrics/baselines |
| G3 | Provide complete baseline implementations | At least 3 baselines per task, covering statistical and deep learning methods |
| G4 | Establish a strict leakage-free evaluation protocol | Temporal splitting + rolling window, with benchmark statistics frozen |
| G5 | Release the benchmark and code | HuggingFace dataset + GitHub repository (Apache-2.0) |
| G6 | Achieve community impact | Paper submission + challenge + community adoption |

## 3. Key Differences from Existing Benchmarks

| Dimension | CubeBench family | WCA-Bench |
| --- | --- | --- |
| Data source | Synthetic scramble states | Real WCA competition data (289k competitors, 6.6M results) |
| Evaluation target | Spatial reasoning and sequence planning | Prediction and inference on sports data |
| Task types | Solving, move-count optimization | Regression, ranking, classification, extreme value estimation, causal inference |
| Time dimension | Static states | Longitudinal tracking (competitor careers) |
| Domain rules | Cube turn rules | WCA competition regulations (round formats, DNF handling, multi-blind encoding) |
| Evaluated subjects | LLM agents | Classical ML models, deep learning models, statistical models |

## 4. Target Users

| Audience | How they use it |
| --- | --- |
| ML / statistics researchers | Evaluate new methods on standardized tasks and compare against prior work |
| Sports data analysis researchers | Study non-stationarity, rare events, and causal effects in longitudinal competitive data |
| WCA community (competitors/organizers) | Analyze individual performance and optimize round settings and advancement rules |
| Benchmark methodology researchers | Study the design of leakage-free protocols, stratified evaluation, and statistical testing |

## 5. Further Reading

- [Project Scope →](/guide/scope)
- [Technical Approach Overview →](/guide/architecture)
- [Expected Outcomes and Success Criteria →](/guide/outcomes)
