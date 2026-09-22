# 计算与硬件

每当介绍本基准时，总会被问到同一个问题：**为什么推理跑在 CPU 而不是 GPU 上？** 本页用**本次参考运行的真实测量结果**回答该问题，列出实际跑在 CUDA 上的组件，并规定算力成本的报告方式。

## 1. 简答

WCA-Bench **并非不使用 GPU** —— 它是**CPU 优先、GPU 只用在确实受益的部分**。

- 参考运行使用 **NVIDIA GeForce RTX 4060 Laptop GPU**，所有基线均以 `--device cuda` 启动。
- **21 个基线中有 4 个确实在 CUDA 上执行**：`lstm`（T1）、`gnn`（T2）、`xgboost_log`（T1）、`xgboost_dnf`（T3）。
- 其余 **17 个表格型基线留在 CPU** —— 其特征矩阵只有 2k–80k 行，瓶颈在**每场比赛的小批量前向 + 规则解码**，属于延迟敏感而非吞吐敏感。
- 每个报告都**逐基线记录**了实际设备，因此上述结论是可核查的，而不是断言 —— 见 §4。

## 2. 参考运行

| 项目 | 取值 |
| --- | --- |
| GPU | NVIDIA GeForce RTX 4060 Laptop GPU，8 GB |
| 计算能力 | 8.9 |
| 驱动 | 610.88 |
| CUDA | 13.0 |
| PyTorch | 2.13.0+cu130 |
| 模式 / 种子 | `small` / 42（单次运行）；42、43、44（多种子） |
| 命令 | `python scripts/run_all_baselines.py --mode small --device cuda` |

下表直接取自各报告记录的解析后设备：

- **在 CUDA 上（4 个）：** `lstm`、`gnn`、`xgboost_log`、`xgboost_dnf`
- **在 CPU 上（17 个）：** `history_mean`、`kde`、`ridge_log`、`psych_sheet`、`plackett_luce`、`kde_simulation`、`historical_dnf_rate`、`logistic`、`beta_binomial`、`exponential_decay`、`changepoint`、`gp_evt`、`hierarchical_shrinkage`、`spearman_correlation`、`did_proxy`、`iv_2sls`、`causal_forest`

## 3. 为什么表格型基线留在 CPU

### 3.1 工作负载是延迟敏感而非吞吐敏感

滚动窗口协议逐场比赛评估：对每场比赛，模型只能看到该场比赛 `as_of` 日期之前可用的数据（见[评估协议与分层](/zh/evaluation/protocol#_1-评估协议)）。因此单次前向的批量**极小**——从几行到几百行。

真正的开销并不在矩阵代数上，而在于：

- 每场比赛的特征构造；
- 小批量前向计算；
- 以及**规则解码**（多盲解码、ao5 去极值、名次重建、DNF 统计）。

GPU 的优势体现在大矩阵乘法吞吐上。在当前算子规模下，内核启动开销与主机↔设备传输反而成为主导，把表格型基线搬到 GPU 通常是净亏损。实测挂钟时间也印证了这一点：

| 基线 | 设备 | `wall_clock_sec` |
| --- | --- | --- |
| `beta_binomial` | cpu | ≈ 0.0024 |
| `gp_evt` | cpu | ≈ 0.026 |
| `psych_sheet` | cpu | ≈ 0.76 |
| `lstm` | cuda | ≈ 31.39 |

即便是**最慢的 GPU 基线**，其绝对耗时也高于一个典型 CPU 基线——原因是它每个样本要做的计算多得多，而不是设备的问题。

### 3.2 CPU 侧的开销主要来自宽口径因果估计器

本次运行中最慢的基线是 CPU 上的因果估计器——`iv_2sls`（≈ 312.8 秒）、`causal_forest`（≈ 245.2 秒）、`did_proxy`（≈ 38.5 秒）。其成本来自项目两两交叉问题的规模（17 × 17 组、80 000 条观测），与设备无关。这恰恰是 §6 所述「批量化」的适用场景，与是否上 GPU 是两个正交的问题。

### 3.3 可复现性

CPU 执行消除了一整类非确定性：没有 cuDNN 内核选择、没有设备相关的浮点归约顺序、不依赖驱动版本。正因如此，**默认仍是 `cpu`**，尽管参考运行使用了 CUDA。

## 4. 成本报告规范

每份报告都带有 `cost` 字段。字段如下：

| 字段 | 含义 | 出现条件 |
| --- | --- | --- |
| `device` | 解析后的设备，如 `cpu` 或 `cuda:NVIDIA GeForce RTX 4060 Laptop GPU` | 始终 |
| `wall_clock_sec` | 该基线的端到端挂钟时间 | 始终 |
| `cpu_hours` | 上述时间跨度折算为小时 | 始终 |
| `gpu_hours` | 消耗的设备时间 | 仅 GPU 基线 |
| `gpu_model` | 加速器型号 | 仅 GPU 基线 |

以下片段直接复制自已提交的报告。

`examples/placement__gnn.json`：

```json
"cost": {
  "mode": "small",
  "baseline_kind": "method",
  "device": "cuda:NVIDIA GeForce RTX 4060 Laptop GPU",
  "wall_clock_sec": 1.170491500000935,
  "cpu_hours": 0.00032513652777803754,
  "gpu_hours": 0.00032513652777803754,
  "gpu_model": "NVIDIA GeForce RTX 4060 Laptop GPU"
}
```

`examples/result_prediction__lstm.json`：

```json
"cost": {
  "mode": "small",
  "baseline_kind": "method",
  "device": "cuda:NVIDIA GeForce RTX 4060 Laptop GPU",
  "wall_clock_sec": 31.385063900001114,
  "cpu_hours": 0.008718073305555865,
  "gpu_hours": 0.008718073305555865,
  "gpu_model": "NVIDIA GeForce RTX 4060 Laptop GPU"
}
```

CPU 基线只报告前三个字段，例如 `examples/placement__psych_sheet.json`：

```json
"cost": {
  "mode": "small",
  "baseline_kind": "domain",
  "device": "cpu",
  "wall_clock_sec": 0.7611801000002743,
  "cpu_hours": 0.00021143891666674285
}
```

> 对 GPU 基线而言 `cpu_hours` 与 `gpu_hours` 数值相同，因为所报告的时间跨度就是该次运行的挂钟时间，并被归属到执行它的设备上。这两个字段用于可比性，而非能耗核算。

以上是**报告级**字段。**提交级**的 `cost.json` 会跨训练与推理聚合同样的量，并补充单样本延迟；见[复现性要求 · 算力成本报告](/zh/evaluation/reproducibility#_4-算力成本报告)与[排行榜提交格式](/zh/evaluation/reproducibility#_7-排行榜提交格式)。

报告必须同时给出**性能与成本**，避免「用 100 倍算力换来 1% 提升」被隐藏。

## 5. 可以使用 GPU 的组件

| 组件 | 包 | GPU 路径 |
| --- | --- | --- |
| LSTM（T1 成绩预测） | `baselines/deep/` | torch 设备选择 |
| GNN（T2 名次预测） | `baselines/graph/` | torch 设备选择 |
| XGBoost（T1 / T3） | `baselines/tree/` | 在支持 CUDA 的 XGBoost 构建上使用 `device="cuda"` |

因此基于 torch 的基线与基于 boosting 的基线都真正用到了 GPU；统计、排序、贝叶斯与因果基线没有。

### 5.1 如何选择设备

`wca_bench.utils.device.resolve_device()` 统一该决策：

| 传入值 | 解析结果 |
| --- | --- |
| `None`（默认） | 若设置了 `WCA_BENCH_DEVICE` 则用之，否则 **`cpu`** |
| `"cpu"` | `cpu` |
| `"cuda"` / `"cuda:<idx>"` | 对应 CUDA 设备；若 torch/CUDA 不可用则退化为 `cpu` |
| `"auto"` | CUDA 确实可用时用 `cuda`，否则 `cpu` |

两种指定方式：

- **命令行参数** —— 所有运行脚本都接受 `--device {auto,cpu,cuda}`，例如 `python scripts/run_all_baselines.py --mode small --device cuda`。
- **环境变量** —— `set WCA_BENCH_DEVICE=cuda`（Windows）或 `export WCA_BENCH_DEVICE=cuda`（bash），在未显式指定设备时生效。

`device_label()` 生成写入报告的可读标签，如 `cuda:NVIDIA GeForce RTX 4060 Laptop GPU` 或 `cpu`。

**默认为 `cpu`**，因此不带参数运行可在任何机器上复现。想机会性地使用 CUDA 可用 `--device auto`，要求必须使用 CUDA 则用 `--device cuda`。

## 6. 什么时候值得上 GPU

值得上 GPU 的时机是**总体工作量**增长，而不是单次计算的规模增长：

- 在完整测试窗口上做全量滚动窗口扫描，**乘以多个种子**，**再乘以**深度 / 图 / boosting 基线；
- 对 `baselines/deep/`、`baselines/graph/`、`baselines/tree/` 做反复的超参搜索。

多种子运行正是这一场景：`python scripts/run_multi_seed.py --seeds 42 43 44 --mode small --device cuda`，产出 `examples/multi_seed.md`。

真的走到这一步时，建议：

1. **把 `as_of` 日期相同的比赛合并成批。** 协议禁止使用更晚比赛的信息，因此构造大 batch 的安全做法是把**决策日期相同**的所有比赛分到一组一起跑。防泄漏性得以保持——`assert_no_leakage` 依然作用于合并后的批次——同时给加速器足够的矩阵规模。
2. **保持滚动窗口语义。** 绝不把 `as_of` 不同的比赛混入同一批，即便那样更快。
3. **如实报告设备。** 给出 `device`、`gpu_hours` 与 `gpu_model`，并说明排行榜其余部分是否产自 CPU；混设备的排行榜必须显式标注。
4. **不要期待批量化改变结论。** 设备选择影响的是运行时，而非方法排序——这正是把 `cpu` 作为默认、并让已公布数字保持可比的原因。

## 7. 后续阅读

- [复现性要求 · 算力成本报告](/zh/evaluation/reproducibility#_4-算力成本报告)
- [任务套件 · 基线清单](/zh/tasks/#_5-基线清单)
- [任务套件 · 观测结果](/zh/tasks/#_5-3-观测结果-seed-42)
- [任务套件 · 多种子稳定性](/zh/tasks/#_5-4-多种子稳定性)
- [评估协议与分层](/zh/evaluation/protocol#_1-评估协议)
- [开发计划 · 目录组织与文档分层](/zh/plan/structure)
