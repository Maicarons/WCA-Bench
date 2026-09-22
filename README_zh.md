# WCA-Bench

**基于世界魔方协会比赛成绩数据库构建的标准化体育数据分析基准。**

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)](pyproject.toml)
[![Tasks](https://img.shields.io/badge/tasks-5-brightgreen.svg)](#五个任务)
[![Docs](https://img.shields.io/badge/docs-VitePress-42b883.svg)](docs/)
[![Paper](https://img.shields.io/badge/paper-arXiv%20XeLaTeX-b31b1b.svg)](paper/)
[![English](https://img.shields.io/badge/lang-English-blue.svg)](README.md)

WCA-Bench 是首个基于**世界魔方协会（WCA）全量公开比赛记录**构建的综合性机器学习基准。它定义了五个核心任务——成绩预测、名次预测、DNF 预测、人类极限估计、技能迁移分析——并提供严格防泄漏的评估协议与可复现的实验框架。

---

## 目录

- [为什么需要 WCA-Bench](#为什么需要-wca-bench)
- [核心特征](#核心特征)
- [快速开始](#快速开始)
- [仓库结构](#仓库结构)
- [五个任务](#五个任务)
- [评估协议](#评估协议)
- [基线与示例结果](#基线与示例结果)
- [数据](#数据)
- [复现性](#复现性)
- [文档](#文档)
- [发布](#发布)
- [论文](#论文)
- [引用](#引用)
- [许可证与数据署名](#许可证与数据署名)
- [贡献](#贡献)

---

## 为什么需要 WCA-Bench

基于 WCA 数据的机器学习研究存在三个突出问题：

1. **研究碎片化。** 已有工作分散在单一任务上（核密度估计名次、线性回归外推世界纪录、高斯过程 + 极值理论估计人类极限），各自采用不兼容的划分方式、指标与预处理流程，结果无法横向比较。
2. **缺乏标准化评估。** *CubeBench* 系列基准评估的是**魔方求解**——LLM 智能体的空间推理与序列规划能力，无法回答关于真实比赛数据预测与推断能力的问题。
3. **领域特定结构被忽视。** WCA 数据具有通用时序模型难以直接处理的特性：选手纵向职业生涯、跨项目技能迁移、轮次格式（average of 5、mean of 3）、哨兵值编码（`-1` DNF、`-2` DNS）、多盲编码（`1SSAATTTTT` / `0DDTTTTTMM`），以及会放大单次 DNF 影响的去极值规则。

WCA-Bench **不是**一个新的预测模型，而是定义一个评估问题：*在竞技体育数据的真实约束下，不同方法论家族（传统统计、深度学习、图学习、生成模型）的表现如何？*

| 维度 | CubeBench 系列 | **WCA-Bench** |
| --- | --- | --- |
| 数据来源 | 合成打乱状态 | WCA 真实比赛记录 |
| 评估目标 | 空间推理与序列规划 | 体育数据的预测与推断能力 |
| 任务类型 | 求解、步数优化 | 回归、排序、分类、极值估计、因果推断 |
| 时间维度 | 静态状态 | 纵向职业生涯追踪（2003–2026） |
| 领域规则 | 魔方转动语义 | WCA 竞赛规则与编码 |
| 评估对象 | LLM 智能体 | 统计 / ML / DL 模型 |

---

## 核心特征

| 维度 | WCA-Bench 提供的内容 |
| --- | --- |
| **数据** | 官方 WCA Results Export v2.0.2 —— 约 690 万条成绩、约 29.8 万名选手、约 1.87 万场比赛，覆盖 17 个现役项目与已废止项目 |
| **任务** | 五个任务，构成从回归到因果推断的连续难度谱 |
| **协议** | 时间分割 + 滚动窗口评估 + 冻结基准统计量，杜绝未来信息泄漏 |
| **分层** | 四维分层报告：按项目、按选手水平、按时间、按大洲 |
| **统计** | 配对 *t* 检验、Bootstrap 置信区间、Friedman + Nemenyi、Cohen's *d* / Cliff's *delta* |
| **基线** | 统计 / 树模型 / 深度 / 图 / 贝叶斯 / 因果六大类，统一接口运行 |
| **复现性** | 固定随机种子、YAML 驱动实验、离线合成数据通路、提交校验脚本 |
| **治理** | 数据卡（含允许/禁止用途）、贡献指南、行为准则、CITATION |
| **国际化** | 英文为主语言，提供完整简体中文文档（`README_zh.md`、`/zh/` 文档站） |

---

## 快速开始

### 安装

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
# source .venv/bin/activate       # macOS / Linux

# 核心 + 开发 + 可选加速依赖
pip install -e ".[dev,fast,boost]"
```

可选重型依赖：

```bash
pip install -e ".[deep]"          # 基于 torch 的序列 / 图基线
```

### 离线端到端（合成数据，CI 使用）

```bash
python scripts/generate_synthetic.py --small
python scripts/build_dataset.py --source synthetic
python scripts/run_all_baselines.py --mode small
python scripts/build_leaderboard.py
pytest
```

### 真实 WCA 数据

```bash
python scripts/download_data.py                 # 拉取官方 TSV 导出
python scripts/build_dataset.py --source raw    # 解码、特征、划分、冻结统计量
python scripts/run_all_baselines.py --mode full
python scripts/build_leaderboard.py
```

构建文档站点：

```bash
npm install
npm run docs:dev      # http://localhost:5173
npm run docs:build    # 静态站点 -> docs/.vitepress/dist
```

---

## 仓库结构

```text
wca-bench/
├── src/wca_bench/          # Python 主包
│   ├── data/               # 加载、解码、特征、划分、合成数据
│   ├── tasks/              # 统一 Task 接口 + T1–T5 适配
│   ├── baselines/          # statistical / tree / deep / graph / bayesian / causal
│   ├── evaluation/         # 指标、滚动协议、分层、显著性
│   ├── leaderboard/        # 报告聚合
│   └── utils/              # io、日志、随机种子
├── configs/                # YAML 实验配置（每个基线一份）
├── scripts/                # 下载、构建、运行、校验、排行榜
├── tests/                  # 单元测试 + 集成测试
├── docs/                   # VitePress 文档站（英文 + 中文 locale）
├── examples/               # 基线报告、排行榜、提交模板
├── publish/                # Hugging Face 与 ModelScope 发布物料与脚本
├── paper/                  # arXiv 格式 XeLaTeX 论文
├── datacard.md             # 数据卡
├── LICENSE                 # Apache-2.0
└── pyproject.toml
```

---

## 五个任务

| ID | 任务 | 学习范式 | 主指标 | 领域挑战 |
| --- | --- | --- | --- | --- |
| **T1** | 成绩预测 | 回归 | 对数域 MAE / RMSE、区间覆盖率 | 职业生涯非平稳；项目间方差差异大 |
| **T2** | 名次预测 | 排序 | Kendall's τ、前 3 名重叠、Brier 分数 | 选手交互效应；去极值规则放大 DNF 影响 |
| **T3** | DNF 预测 | 不平衡分类 | AUC-ROC、AUC-PR、F1、MCC、校准 | 稀有事件、项目间极不均衡、序列依赖 |
| **T4** | 人类极限估计 | 极值 / 外推 | 留一稳定性、区间覆盖率、领域一致性 | 外推风险；各项目数据密度差异巨大 |
| **T5** | 技能迁移分析 | 因果推断 | 点估计精度、稳健性、专家一致性 | 混淆因素；参赛顺序非随机 |

所有任务遵循同一接口：

```python
class Task(Protocol):
    name: str
    task_type: TaskType

    def split(self) -> dict[str, pd.DataFrame]: ...
    def featurize(self, as_of) -> pd.DataFrame: ...   # as_of 必填：防泄漏
    def metrics(self) -> list[str]: ...
    def baselines(self) -> list[Baseline]: ...
    def evaluate(self, model_name: str, preds=None) -> Report: ...
```

由于 `featurize` 强制要求显式传入 `as_of`，无法构造使用决策时刻及之后信息的特征。

---

## 评估协议

**时间分割（非随机分割）：**

| 集合 | 时间范围 | 用途 |
| --- | --- | --- |
| train | 2003–2022 | 拟合与基准统计量估计 |
| validation | 2023–2024 | 超参调优与模型选择 |
| test | 2025–2026 | 最终评估（固定窗口） |

**滚动窗口评估。** 对每一场测试比赛，模型只能使用严格早于该场比赛的记录。基准统计量——历史均值、世界纪录、选手水平分位阈值——从训练窗口计算一次后在整个测试期**冻结**。

**四维分层** 避免结论被最大子群主导：按项目、按选手水平（新手 / 中级 / 高级 / 精英）、按时间子集（Test-A 2025H1、Test-B 2025H2、Test-C 2026H1）、按大洲。

**统计严谨性。** 所有模型比较均报告配对 *t* 检验、1000 次 Bootstrap 置信区间、多模型比较的 Friedman + Nemenyi，以及效应量（Cohen's *d* 或 Cliff's *delta*）。

**硬样本子集。** 为防止基准饱和，每个任务额外报告硬样本子集（例如 DNF 预测报告历史 DNF 率位于 `[0.1, 0.3]` 的选手）。

完整协议见 [`docs/zh/evaluation/`](docs/zh/evaluation/)。

---

## 基线与示例结果

**21 个基线**覆盖六个家族，全部通过同一条 `Task.evaluate` 路径：

| 家族 | 基线 | 覆盖 |
| --- | --- | --- |
| `statistical` | 历史均值、高斯核密度、Psych Sheet、Plackett–Luce、名次 KDE 模拟、历史 DNF 率、指数衰减、变点检测、GP + 极值 | T1–T5 |
| `tree` | `log(best)` 上的 Ridge、XGBoost 回归、逻辑回归、XGBoost DNF 分类 | T1、T3 |
| `deep` | LSTM 序列模型 *（torch 可选，含优雅降级）* | T1 |
| `graph` | 选手–比赛异构图 GNN *（torch 可选，含优雅降级）* | T2 |
| `bayesian` | Beta–Binomial DNF 模型、分层收缩极限估计 | T3、T4 |
| `causal` | Spearman 相关参照、双重差分、工具变量（2SLS）、因果森林 | T5 |

真实 WCA 导出 v2.0.2 上的抽样运行结果（抽样测试窗口，seed 42，**CUDA**）见
[`examples/leaderboard.md`](examples/leaderboard.md)；多种子均值见
[`examples/multi_seed.md`](examples/multi_seed.md)。

| 任务 | 抽样最佳基线 | 主指标 | 多种子（42/43/44） |
| --- | --- | --- | --- |
| T1 成绩预测 | `xgboost_log` | MAE(log) ↓ 0.164 | 0.106 ± 0.042 |
| T2 名次预测 | `kde_simulation` / `plackett_luce` / `psych_sheet` | Kendall τ ↑ 0.767 | 0.813 ± 0.034 |
| T3 DNF 预测 | `xgboost_dnf` | AUC-PR ↑ 0.373 | `beta_binomial` 0.294 ± 0.057 |
| T4 人类极限 | `gp_evt` | 留一稳定性 ↓ 0.98 | 0.984 ± 0.000 |
| T5 技能迁移 | `spearman_correlation` | 413 个可识别项目对 | 413 |

两个值得注意的发现：

1. **领域感知基线优于通用深度与图模型。** T1 上 LSTM（MAE(log) 0.944 ± 0.075）远差于梯度提升树（0.106 ± 0.042）；T2 上 GNN（τ 0.744 ± 0.126）低于规则感知的 Psych Sheet 基线（0.813 ± 0.034）。
2. **接近的竞争者在不同评估窗口下会换位。** T3 单次运行偏向 `xgboost_dnf`（0.373），而多种子均值偏向 `beta_binomial`（0.294 ± 0.057 对 0.278 ± 0.072）——这正是必须报告多种子的原因。

### 计算与硬件

- 表格型基线（KDE、Plackett–Luce、Beta–Binomial、GP + EVT、DID/IV、因果森林）**默认在 CPU 上运行**：工作集仅 2k–80k 行，瓶颈是「每场比赛的小批量前向 + 规则解码」，属延迟敏感而非吞吐敏感。
- **LSTM 与 GNN 基线在 CUDA 上训练**，梯度提升基线也可置于 GPU。上述结果产自 **NVIDIA GeForce RTX 4060 Laptop GPU（8 GB）**、CUDA 13.0、torch 2.13.0+cu130。
- 每个报告都记录实际使用的设备：`device`（`cpu` 或 `cuda:<型号>`）、`wall_clock_sec`、`cpu_hours`，在 GPU 上另有 `gpu_hours` 与 `gpu_model`。
- 通过 `--device {auto,cpu,cuda}` 或环境变量 `WCA_BENCH_DEVICE` 选择设备；默认保持 `cpu`，以保证小规模运行逐位可复现。

> 完整排行榜需在滚动窗口协议下用全量数据重跑。以上数字来自可快速完成的抽样模式，已明确标注。

---

## 数据

WCA-Bench 提供两条数据通路：

- **真实数据** —— `scripts/download_data.py` 拉取官方 WCA Results Export（v2.0.2）。`scripts/build_dataset.py --source raw` 负责解码成绩、归一化轮次格式、构建特征、应用时间分割并冻结基准统计量。产物以 Parquet 落盘到 `data/processed/` 与 `data/splits/`。
- **合成数据** —— `scripts/generate_synthetic.py` 生成小规模 WCA 风格导出，使 CI 与离线开发无需联网。

解码规则显式且可测试：`time` 值为百分之一秒，`number` 值为步数，多盲成绩使用 `1SSAATTTTT` / `0DDTTTTTMM` 编码，`-1` 为 DNF，`-2` 为 DNS，`0` 表示无成绩。Average of 5 的重建遵循官方的「去除最优与最差」规则。

全部使用约束记录在 [`datacard.md`](datacard.md)（中文版见 [`datacard_zh.md`](datacard_zh.md)），包括禁止赌博或投注预测、歧视性画像，以及任何冒充官方机构的行为。

---

## 复现性

- 所有实验由 [`configs/`](configs/) 下的 YAML 驱动，可单命令复跑。
- 随机种子固定（`utils/seed.py`），并在每份报告中记录。
- 支持多种子运行：`python scripts/run_multi_seed.py --seeds 42 43 44 --mode small`。
- 报告遵循统一 schema：`overall`、`stratified`、`hard_subset`、`significance`、`cost`、`extras`。
- 提交材料用 `python scripts/validate_submission.py <submission_dir>` 校验；骨架见 `examples/submission_template/`。
- 复现等级定义：**L1**（可重跑）、**L2**（结果在容差内一致）、**L3**（原始预测可下载、指标可独立重算）。主排行榜要求 L3。

---

## 文档

文档站点使用 **VitePress** 构建，支持双语。

| 层级 | English | 中文 |
| --- | --- | --- |
| 项目计划书 | `docs/guide/` | `docs/zh/guide/` |
| 技术方案 | `docs/data/`、`docs/tasks/`、`docs/evaluation/` | `docs/zh/...` |
| 开发计划 | `docs/plan/` | `docs/zh/plan/` |

建议先读 [`docs/zh/guide/`](docs/zh/guide/)（项目计划书）与 [`docs/zh/plan/`](docs/zh/plan/)（开发计划、里程碑、依赖关系、验收标准）。

---

## 发布

面向两大模型社区的发布物料位于 [`publish/`](publish/)：

```bash
python publish/tools/stage_release.py --tier core --dry-run   # 组装发布目录树
python publish/huggingface/upload_dataset.py --dry-run        # Hugging Face Hub
python publish/modelscope/upload.py --dry-run                 # ModelScope
python publish/tools/make_archive.py                          # tar.gz + SHA256SUMS
```

Token 从环境变量 `HF_TOKEN` 与 `MODELSCOPE_API_TOKEN` 读取，绝不写入文件。

---

## 论文

[`paper/`](paper/) 提供了可直接编译、符合 arXiv 要求的 XeLaTeX 论文：

```bash
cd paper
make            # 或：latexmk -xelatex main.tex
make figures    # 从 examples/leaderboard.csv 重新生成图表
```

TeX Live 依赖与打包说明见 [`paper/README.md`](paper/README.md)。

---

## 引用

```bibtex
@misc{wcabench2026,
  title        = {WCA-Bench: A Sports Analytics Benchmark from World Cube Association Competition Data},
  author       = {{WCA-Bench Project}},
  year         = {2026},
  version      = {0.1.0},
  howpublished = {\url{https://github.com/Maicarons/WCA-Bench}},
  note         = {Dataset and benchmark}
}
```

机器可读元数据见 [`CITATION.cff`](CITATION.cff)。

---

## 许可证与数据署名

- **代码** 以 [Apache License 2.0](LICENSE) 发布。
- **数据** 由世界魔方协会拥有与维护。再发布任何源自 WCA 导出的信息时，必须保留官方署名：

  > This information is based on competition results owned and maintained by the World Cube Association, published at https://worldcubeassociation.org/results

- 使用约束（含禁止用途）见 [`datacard_zh.md`](datacard_zh.md)。

---

## 贡献

欢迎贡献。请先阅读 [`CONTRIBUTING_zh.md`](CONTRIBUTING_zh.md) 与 [`CODE_OF_CONDUCT_zh.md`](CODE_OF_CONDUCT_zh.md)。

关键规则：

- 依赖方向单向：`tasks → data`、`baselines → tasks → data`、`evaluation → tasks + data`、`leaderboard → evaluation`。`data` 包**不得** import `tasks`、`baselines`、`evaluation`、`leaderboard`（由 `tests/unit/test_import_policy.py` 强制校验）。
- 每个 PR 必须通过 lint、单元测试、合成数据端到端运行、文档站构建与防泄漏断言。
- 任何对任务定义或评估协议的修改，必须在同一个 PR 中同步更新 `docs/`。

---

[English](README.md) · [简体中文](README_zh.md)
