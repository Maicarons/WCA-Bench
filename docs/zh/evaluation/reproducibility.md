# 复现性要求

## 1. 提交清单

所有提交的模型**必须**提供：

- [ ] 完整的**训练代码**和**随机种子**
- [ ] **数据预处理脚本**（或引用基准管线版本）
- [ ] **模型权重**的 HuggingFace 托管链接
- [ ] **推理时间的计算成本报告**（GPU 小时或 CPU 小时）

## 2. 环境与版本

| 项目 | 要求 |
| --- | --- |
| Python 版本 | 在 `pyproject.toml` / `environment.yml` 中固定 |
| 依赖版本 | 锁定（lockfile 或精确版本号） |
| 数据快照 | 记录 WCA 导出快照版本号（如 v2.0.2） |
| 硬件 | 记录 GPU / CPU 型号与数量 |
| 随机性 | 固定所有随机源（Python、NumPy、PyTorch、CUDA） |

## 3. 随机种子策略

```python
def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
```

要求：

- 主结果至少报告 **3 个种子**的均值 ± 标准差 —— *已满足*：种子 **42 / 43 / 44**，由 `scripts/run_multi_seed.py --device cuda` 聚合为 `examples/multi_seed.md`
- 报告中显式给出使用的种子列表
- Bootstrap / 蒙特卡洛模拟的种子同样固定

多种子产物覆盖五任务下全部 21 个基线，已提交为 `examples/multi_seed.md`（机器可读输出：`outputs/multi_seed/multi_seed.json`）。由于种子决定从测试窗口中抽取哪些比赛，报告中的离散度度量的是**评估窗口的抽样方差**，而非训练不稳定性；T4（在固定世界纪录序列上的确定性估计）与 T5（基于完整训练历史计算）相应地跨种子稳定。主要数字汇总于[任务套件 · 多种子稳定性](/zh/tasks/#_5-4-多种子稳定性)。

## 4. 算力成本报告

```json
{
  "task": "result_prediction",
  "training": {"hardware": "A100-40G", "gpu_hours": 12.5, "wall_clock_hours": 2.1},
  "inference": {"hardware": "A100-40G", "gpu_hours": 0.3, "per_sample_ms": 4.2},
  "total": {"gpu_hours": 12.8}
}
```

对比基线时，需同时给出**性能与成本的权衡**，避免「用 100 倍算力换来 1% 提升」被隐藏。

报告记录解析后的 `device`、挂钟时间与 CPU 小时；若使用 GPU，还会额外记录 `gpu_hours` 与加速器型号。CPU 优先的默认选择及其理由、完整字段列表、以及何时值得上 GPU，见[计算与硬件](/zh/evaluation/compute)；字段级规范见[计算与硬件 · 成本报告规范](/zh/evaluation/compute#_4-成本报告规范)。

## 5. 产物与校验

| 产物 | 校验方式 |
| --- | --- |
| 预处理 Parquet | 记录行数、列名、校验和（SHA256） |
| 分割索引 | 与原始表行数对账 |
| 模型权重 | 记录文件校验和与训练配置 |
| 预测结果 | 保存每场比赛的原始预测，便于重算指标 |

## 6. 复现等级

| 等级 | 定义 |
| --- | --- |
| L1 可重跑 | 代码可运行，脚本齐全 |
| L2 可复现 | L1 + 结果在容差内一致（±1% 指标） |
| L3 可验证 | L2 + 原始预测可下载，指标可独立重算 |

**基准收录的最低要求为 L2；主排行榜要求 L3。**

## 7. 排行榜提交格式

```text
submission/
├── report/               # 见评估框架的报告模板
├── predictions.parquet   # 每场比赛的原始预测
├── config.yaml           # 模型与训练配置
├── environment.yml       # 环境锁定
├── seeds.json            # 随机种子
├── cost.json             # 算力报告
└── README.md             # 复现步骤
```

社区条目使用同一个信息的**扁平报告 JSON**（`{task}__{model}.json`），放在
`community-submissions/` 下。结构与校验命令见
[community-submissions/README.md](https://github.com/Maicarons/WCA-Bench/blob/main/community-submissions/README.md)，
完整流程（含通过排行榜 Space 提交）见[参与排行榜](/zh/guide/participate)。

## 8. 后续阅读

- [评估框架 · 总览 →](/zh/evaluation/)
- [开发计划 · 验收标准 →](/zh/plan/acceptance)
