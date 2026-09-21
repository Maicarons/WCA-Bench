# 任务套件 · 总览

WCA-Bench 包含五个核心任务，覆盖从**基础预测**到**高级推断**的不同难度层级。

## 1. 任务矩阵

| 编号 | 任务 | 学习范式 | 核心指标 | 领域挑战 |
| --- | --- | --- | --- | --- |
| [T1](/tasks/result-prediction) | 成绩预测 | 回归 | MAE / RMSE（对数域）+ 校准误差 | 表现非平稳性、项目间方差差异 |
| [T2](/tasks/placement) | 名次预测 | 排序 | Kendall's τ、前 3 准确率、Brier | 选手交互效应、去极值机制放大 DNF 影响 |
| [T3](/tasks/dnf) | DNF 预测 | 不平衡二分类 | AUC-ROC/PR、F1、MCC | 稀有事件、项目间极不均匀、序列依赖 |
| [T4](/tasks/limit) | 人类极限估计 | 极值 / 外推 | 稳定性、区间覆盖率、领域一致性 | 外推风险、数据密度差异巨大 |
| [T5](/tasks/transfer) | 技能迁移分析 | 因果推断 | 点估计精度、稳健性、专家一致性 | 混淆因素、参赛顺序非随机 |

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

## 5. 后续阅读

- [任务一：成绩预测 →](/tasks/result-prediction)
- [任务二：名次预测 →](/tasks/placement)
- [任务三：DNF 预测 →](/tasks/dnf)
- [任务四：人类极限估计 →](/tasks/limit)
- [任务五：技能迁移分析 →](/tasks/transfer)
