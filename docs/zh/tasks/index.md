# 任务套件 · 总览

WCA-Bench 包含五个核心任务，覆盖从**基础预测**到**高级推断**的不同难度层级。

## 1. 任务矩阵

| 编号 | 任务 | 学习范式 | 核心指标 | 领域挑战 |
| --- | --- | --- | --- | --- |
| [T1](/zh/tasks/result-prediction) | 成绩预测 | 回归 | MAE / RMSE（对数域）+ 校准误差 | 表现非平稳性、项目间方差差异 |
| [T2](/zh/tasks/placement) | 名次预测 | 排序 | Kendall's τ、前 3 准确率、Brier | 选手交互效应、去极值机制放大 DNF 影响 |
| [T3](/zh/tasks/dnf) | DNF 预测 | 不平衡二分类 | AUC-ROC/PR、F1、MCC | 稀有事件、项目间极不均匀、序列依赖 |
| [T4](/zh/tasks/limit) | 人类极限估计 | 极值 / 外推 | 稳定性、区间覆盖率、领域一致性 | 外推风险、数据密度差异巨大 |
| [T5](/zh/tasks/transfer) | 技能迁移分析 | 因果推断 | 点估计精度、稳健性、专家一致性 | 混淆因素、参赛顺序非随机 |

## 2. 难度谱

```text
易  ┌─── T1 成绩预测（数据充足、指标明确）
    │
    ├─── T3 DNF 预测（类别不平衡，但监督信号清晰）
    │
    ├─── T2 名次预测（需建模选手交互与规则效应）
    │
    ├─── T4 人类极限估计（需外推，无直接监督）
    │
难  └─── T5 技能迁移分析（因果识别，需处理混淆）
```

## 3. 统一任务接口

为保证「同一份评估代码评估所有模型」，所有任务遵循统一约定：

```python
class Task:
    name: str
    task_type: Literal["regression", "ranking", "classification", "extreme", "causal"]

    def split(self) -> SplitView: ...        # 时间分割视图
    def featurize(self, as_of) -> Features:  # 强制传入决策时刻
        ...
    def metrics(self) -> list[Metric]: ...   # 标准指标集合
    def baseline(self) -> list[Baseline]: ...# 注册基线
    def evaluate(self, model) -> Report: ... # 返回指标 + 分层结果
```

关键设计：

- `featurize(as_of)` 的 `as_of` 参数**强制**防泄漏
- `evaluate` 统一返回含**分层结果**与**统计检验**的 `Report`
- 所有基线通过同一 `Report` 可比较

## 4. 基线的分层设计

每个任务至少提供三类基线，构成有意义的对比谱：

| 类型 | 作用 |
| --- | --- |
| 平凡基线（Trivial） | 建立下界（如历史均值、全局多数类） |
| 领域基线（Domain） | 反映当前实践（如 WCA Psych Sheet、历史 DNF 率） |
| 方法论基线（Method） | 检验复杂方法的增益（DL / GNN / 贝叶斯 / 因果） |

实际交付的基线清单 —— **21 个基线** —— 见 §5；每个任务实际提供 4–5 个基线。

## 5. 基线清单

本基准提供 **21 个基线、覆盖 6 个方法论家族** —— 每个家族对应 `src/wca_bench/baselines/` 下的一个子包。所有基线均由 `baselines/__init__.py` 导出、由 `configs/*.yaml` 驱动、经滚动窗口协议运行，并落盘为 `examples/` 下的报告。

| 家族（`baselines/`） | 基线 | 数量 |
| --- | --- | --- |
| `statistical/` | `history_mean`、`kde`、`kde_simulation`、`psych_sheet`、`plackett_luce`、`historical_dnf_rate`、`exponential_decay`、`changepoint`、`gp_evt` | 9 |
| `tree/` | `ridge_log`、`xgboost_log`、`logistic`、`xgboost_dnf` | 4 |
| `bayesian/` | `beta_binomial`、`hierarchical_shrinkage` | 2 |
| `deep/` | `lstm` | 1 |
| `graph/` | `gnn` | 1 |
| `causal/` | `spearman_correlation`、`did_proxy`、`iv_2sls`、`causal_forest` | 4 |
| **合计** | | **21** |

### 5.1 各任务基线清单

| 任务 | 基线 |
| --- | --- |
| [T1 成绩预测](/zh/tasks/result-prediction) | `history_mean`、`kde`、`ridge_log`、`xgboost_log`、`lstm` |
| [T2 名次预测](/zh/tasks/placement) | `psych_sheet`、`plackett_luce`、`kde_simulation`、`gnn` |
| [T3 DNF 预测](/zh/tasks/dnf) | `historical_dnf_rate`、`logistic`、`xgboost_dnf`、`beta_binomial` |
| [T4 人类极限估计](/zh/tasks/limit) | `exponential_decay`、`changepoint`、`gp_evt`、`hierarchical_shrinkage` |
| [T5 技能迁移分析](/zh/tasks/transfer) | `spearman_correlation`、`did_proxy`、`iv_2sls`、`causal_forest` |

因此每个任务都超过计划要求的「每任务 ≥ 3 个基线」，总数 21 个也超过计划的 ≥ 18 目标。

### 5.2 运行基线

```bash
python scripts/run_all_baselines.py --mode small --device cuda   # 抽样测试集
python scripts/build_leaderboard.py                              # -> examples/leaderboard.{md,csv,json}
python scripts/run_multi_seed.py --seeds 42 43 44 --device cuda  # 跨种子均值 ± 标准差
```

设备选择（`--device auto|cpu|cuda`、`WCA_BENCH_DEVICE`）与成本报告约定见[计算与硬件](/zh/evaluation/compute)。

### 5.3 观测结果（seed 42）

已提交的排行榜是在参考 GPU 上以 seed 42 单次 `small` 模式运行的结果。完整表格见 `examples/leaderboard.md`、`examples/leaderboard.csv`、`examples/leaderboard.json`。

| 任务 | 最佳基线 | 主指标 | 值 |
| --- | --- | --- | --- |
| T1 成绩预测 | `xgboost_log` | MAE(log) ↓ | 0.1639 |
| T2 名次预测 | `kde_simulation` / `plackett_luce` / `psych_sheet` | Kendall's τ ↑ | 0.7673 |
| T3 DNF 预测 | `xgboost_dnf` | AUC-PR ↑ | 0.3731 |
| T4 人类极限估计 | `gp_evt` | 留一稳定性 ↓ | 0.9836 |
| T5 技能迁移 | `spearman_correlation` | 可识别项目对 | 413 |

全部排序：

| 任务 | 基线（主指标） | n |
| --- | --- | --- |
| T1 | `xgboost_log` 0.1639 · `history_mean` 0.6657 · `kde` 0.6657 · `ridge_log` 1.0068 · `lstm` 1.0440，均为 MAE(log) | 2196 |
| T2 | `kde_simulation` / `plackett_luce` / `psych_sheet` 0.7673 · `gnn` 0.5670，均为 Kendall's τ | 2260 |
| T3 | `xgboost_dnf` 0.3731 · `beta_binomial` 0.3725 · `historical_dnf_rate` 0.3591 · `logistic` 0.2290，均为 AUC-PR | 2260 |
| T4 | `gp_evt` 0.9836 · `exponential_decay` 6485301.0137 · `hierarchical_shrinkage` 9260100.3746 · `changepoint` 无值，均为留一稳定性 | — |
| T5 | `spearman_correlation` 413 · `causal_forest` 312 · `iv_2sls` 270 · `did_proxy` 6，均为可识别项目对 | 80000 |

这些数字是**示意性的、非最终结果**：`--mode small` 会在测试窗口内随机抽取少量比赛并对训练集做代表性子抽样，因此公开排行榜必须在全量数据与滚动窗口协议下重跑。

### 5.4 多种子稳定性

主指标在种子 **42 / 43 / 44** 上的聚合结果（`scripts/run_multi_seed.py --device cuda`）。完整表格见 `examples/multi_seed.md`。由于种子决定从测试窗口中抽取哪些比赛，下方的离散度度量的是**评估窗口的抽样方差**，而非训练不稳定性。

| 任务 | 模型 | 指标 | 均值 ± 标准差 |
| --- | --- | --- | --- |
| T1 | `xgboost_log` | MAE(log) | 0.1055 ± 0.0417 |
| T1 | `history_mean` / `kde` | MAE(log) | 0.4003 ± 0.1945 |
| T1 | `ridge_log` | MAE(log) | 0.9381 ± 0.0526 |
| T1 | `lstm` | MAE(log) | 0.9436 ± 0.0754 |
| T2 | `psych_sheet` / `plackett_luce` / `kde_simulation` | Kendall's τ | 0.8132 ± 0.0342 |
| T2 | `gnn` | Kendall's τ | 0.7440 ± 0.1258 |
| T3 | `beta_binomial` | AUC-PR | 0.2938 ± 0.0570 |
| T3 | `xgboost_dnf` | AUC-PR | 0.2779 ± 0.0724 |
| T3 | `historical_dnf_rate` | AUC-PR | 0.2631 ± 0.0690 |
| T3 | `logistic` | AUC-PR | 0.1687 ± 0.0429 |
| T4 | `gp_evt` | 留一稳定性 | 0.9836 ± 0.0000 |
| T4 | `exponential_decay` | 留一稳定性 | 6485301.0137 |
| T4 | `hierarchical_shrinkage` | 留一稳定性 | 9260100.3746 |
| T5 | `spearman_correlation` | 可识别项目对 | 413 |
| T5 | `causal_forest` | 可识别项目对 | 312 |
| T5 | `iv_2sls` | 可识别项目对 | 270 |
| T5 | `did_proxy` | 可识别项目对 | 2 |

T4 是在固定世界纪录序列上的确定性估计，T5 的迁移矩阵基于完整训练历史计算，因此两者跨种子稳定（`changepoint` 不产生留一统计量，故省略）。

两个值得注意的发现：

- **领域感知基线优于通用深度与图模型。** T1 上 LSTM（单次 1.0440；多种子 0.9436 ± 0.0754）明显落后于梯度提升树（0.1639；0.1055 ± 0.0417）；T2 上 GNN（0.5670；0.7440 ± 0.1258）落后于规则感知的 Psych Sheet 基线（0.7673；0.8132 ± 0.0342）。
- **排序稳定性因任务而异。** T1、T2 在多种子下保持与单次运行一致的排序，但 T3 不是：单次运行中 `xgboost_dnf` 领先（0.3731），而多种子均值下 `beta_binomial` 反超（0.2938 ± 0.0570 对 0.2779 ± 0.0724）。评估窗口的抽样方差足以让接近的竞争者互换位次——这正是强制多种子报告的原因。

## 6. 后续阅读

- [任务一：成绩预测 →](/zh/tasks/result-prediction)
- [任务二：名次预测 →](/zh/tasks/placement)
- [任务三：DNF 预测 →](/zh/tasks/dnf)
- [任务四：人类极限估计 →](/zh/tasks/limit)
- [任务五：技能迁移分析 →](/zh/tasks/transfer)
