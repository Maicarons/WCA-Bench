# 参与排行榜

WCA-Bench 提供**社区排行榜**：任何人都可以训练自己的模型，在冻结测试集上评测，
并与官方基线一同排名。

> **为什么是自报结果？**
> 部分指标无法仅凭预测文件重算——人类极限估计（T4）依赖留一法稳定性，技能迁移
> 分析（T5）依赖因果推断管线。因此我们不运行参赛者的代码，而是由参赛者本地评测
> 后提交**报告 JSON**。这与[复现性要求](/zh/evaluation/reproducibility)中的复现等级
> 一致：主排行榜要求 **L3（可验证）**，即公开原始预测、指标可被独立重算。

## 1. 获取数据

| 来源 | 链接 |
| --- | --- |
| Hugging Face | [Maicarons/WCA-Bench](https://huggingface.co/datasets/Maicarons/WCA-Bench) |
| ModelScope | [Mai2026/WCA-Bench](https://www.modelscope.cn/datasets/Mai2026/WCA-Bench) |

每行数据都带有 `split` 标记（`train` / `val` / `test`），特征所需的冻结统计量与
其一同发布。

```bash
pip install -e ".[dev,fast,boost]"
```

## 2. 训练与评测

在 `train` 上拟合、在 `val` 上选模、在 `test` 上预测——**绝不能**让测试集标签
进入拟合或调参环节。

```python
import json
from pathlib import Path

from wca_bench.data.loader import load_dataset
from wca_bench.tasks.result_prediction import ResultPredictionTask

data = load_dataset(raw_dir="data/raw", processed_dir="data/processed", build=True)
task = ResultPredictionTask(data)
splits = task.split()          # {"train": ..., "val": ..., "test": ...}

predictions = my_predict(task, splits["test"])   # 你的模型在这里

report = task.evaluate("my_model", predictions)
Path("result_prediction__my_model.json").write_text(
    json.dumps(report.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8"
)
```

切换任务只需导入对应的类：

| 任务 | 类 |
| --- | --- |
| `result_prediction` | `wca_bench.tasks.result_prediction.ResultPredictionTask` |
| `placement` | `wca_bench.tasks.placement.PlacementTask` |
| `dnf` | `wca_bench.tasks.dnf.DNFTask` |
| `limit` | `wca_bench.tasks.limit.HumanLimitTask` |
| `transfer` | `wca_bench.tasks.transfer.SkillTransferTask` |

## 3. 提交

在排行榜 Space 的 **Submit** 标签页上传报告，或直接提 PR 把文件加入
`community-submissions/`。所有提交都会先经过机器校验：

```bash
python scripts/validate_community_submission.py community-submissions
```

接受的结构见
[community-submissions/README.md](https://github.com/Maicarons/WCA-Bench/blob/main/community-submissions/README.md)，
CI 会对每个 PR 执行同一校验。

## 4. 发布已接受的条目

```bash
python scripts/build_leaderboard.py \
  --report-dir examples \
  --with-community \
  --out-dir examples
```

该命令把社区报告与官方基线合并，重写 `examples/leaderboard.{csv,json,md}`；
重新发布数据集后榜单即更新。

## 规则速览

1. 冻结协议：在 `train` 拟合、`val` 选模、`test` 上报。
2. 公开训练代码、随机种子与算力成本（`cost`）。
3. 公开原始预测（L3），使他人可重算指标。
4. 每个 `(task, model)` 一条记录；同名重复提交会更新该行。
5. 维护者会复核可疑结果（例如 `mae_log <= 0`）。
