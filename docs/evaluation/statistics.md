# 统计显著性检验

WCA-Bench 要求所有模型间的比较使用严格的统计检验，避免把随机波动误认为方法增益。

## 1. 检验方法

| 方法 | 用途 | 适用场景 |
| --- | --- | --- |
| **配对 t 检验** | 比较两个模型在同一测试集上的 MAE / RMSE 差异 | 两模型、成对样本 |
| **Bootstrap 置信区间** | 通过 1000 次重采样计算指标的不确定性 | 任意指标、分布未知 |
| **Friedman 检验 + Nemenyi 后检验** | 多模型比较 | ≥ 3 模型、多数据集/多子集 |
| **效应量报告** | 报告 Cohen's d 或 Cliff's delta | 所有比较 |

## 2. 使用约定

### 2.1 配对 t 检验

```python
from scipy.stats import ttest_rel

# 以「每场比赛的误差」为配对单位
stat, p = ttest_rel(errors_model_a, errors_model_b)
```

前提：

- 配对单位统一（推荐按「比赛 × 项目 × 轮次」）
- 报告均值差 + 95% CI + p 值 + 效应量

### 2.2 Bootstrap 置信区间

```python
def bootstrap_ci(values, metric_fn, n_boot=1000, alpha=0.05, seed=42):
    rng = np.random.default_rng(seed)
    stats = [
        metric_fn(rng.choice(values, size=len(values), replace=True))
        for _ in range(n_boot)
    ]
    lo, hi = np.percentile(stats, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return metric_fn(values), lo, hi
```

要求：

- 固定随机种子（写入报告）
- 报告重采样次数（默认 1000）
- 对分层结果同样给出 CI

### 2.3 多模型比较

当比较 ≥ 3 个模型时：

1. **Friedman 检验**判断是否存在显著差异
2. 若显著，使用 **Nemenyi 后检验**进行两两比较
3. 以 **Critical Difference 图**呈现结果

## 3. 效应量

避免仅依赖 p 值。至少报告以下之一：

| 效应量 | 类型 | 解释 |
| --- | --- | --- |
| Cohen's d | 参数 | 0.2 小 / 0.5 中 / 0.8 大 |
| Cliff's delta | 非参数 | \|δ\| < 0.147 可忽略 / < 0.33 小 / < 0.474 中 / 其他大 |

## 4. 报告规范

每项比较必须在 `significance.json` 中给出：

```json
{
  "comparison": "modelA vs PsychSheet",
  "task": "placement",
  "metric": "kendall_tau",
  "paired_unit": "competition_event_round",
  "n_pairs": 18420,
  "mean_diff": 0.043,
  "ci95": [0.031, 0.055],
  "p_value": 1.2e-18,
  "effect_size": {"name": "cohens_d", "value": 0.41},
  "test": "paired_t",
  "seed": 42
}
```

## 5. 常见陷阱

| 陷阱 | 后果 | 规避 |
| --- | --- | --- |
| 未配对（聚合后比较） | 高估显著性 | 使用配对单位 |
| 多次比较未校正 | 假阳性膨胀 | Bonferroni / Nemenyi |
| 只报 p 值不报效应量 | 显著性 ≠ 重要性 | 强制效应量 |
| Bootstrap 不固定种子 | 不可复现 | 记录种子 |
| 忽略分层 | 结论被主导群体掩盖 | 分层 + 检验 |

## 6. 后续阅读

- [复现性要求 →](/evaluation/reproducibility)
- [评估协议与分层 →](/evaluation/protocol)
