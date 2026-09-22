# 贡献指南

感谢你对 WCA-Bench 的关注。本项目定位为**标准化基准**，贡献须优先保障评估协议的一致性与可复现性。

英文主版本见 [`CONTRIBUTING.md`](CONTRIBUTING.md)。

## 开发环境

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux
pip install -e ".[dev,fast,boost]"
```

验证：

```bash
pytest
python scripts/generate_synthetic.py
python scripts/build_dataset.py --source synthetic
python scripts/run_all_baselines.py --mode small
```

## 目录与依赖方向

```text
tasks        ──► data
baselines    ──► tasks ──► data
evaluation   ──► tasks + data
leaderboard  ──► evaluation
```

`src/wca_bench/data` **不得** import `tasks` / `baselines` / `evaluation` / `leaderboard`。
`tests/unit/test_import_policy.py` 会强制检查。

## 提交规范

- 分支：`<type>/<scope>-<desc>`，例如 `feat/dnf-xgboost`
- 提交：Conventional Commits，例如 `feat(dnf): add XGBoost baseline`
- Issue：`<type>: <简述>`，例如 `bug: multi-blind decoding edge case`

## PR 要求

1. 代码评审：至少 1 人 approve。
2. 单元测试通过，核心模块覆盖率不下降。
3. 若修改任务定义 / 评估协议，**必须同步更新 `docs/`**。
4. 不得引入未来信息泄漏：特征函数必须强制传入 `as_of`。
5. 新基线必须产出完整 `report/` 结构，且包含 `significance`。

## 任务定义变更

| 变更类型 | 处理 |
| --- | --- |
| 澄清性（不改语义） | 直接更新，patch 版本 |
| 增补（新增指标/子集） | minor 版本，主指标不变 |
| 破坏性（改输入输出） | major 版本，另立排行榜 |

## 行为准则

请阅读 [`CODE_OF_CONDUCT_zh.md`](CODE_OF_CONDUCT_zh.md)。

## 数据与伦理

- 仅使用 WCA 官方公开导出。
- 禁止用于赌博、个体歧视等场景（见 [`datacard_zh.md`](datacard_zh.md)）。
- 发布处理后数据时保留 WCA 署名说明。
