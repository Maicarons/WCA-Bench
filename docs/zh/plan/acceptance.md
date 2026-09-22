# 验收标准

本章定义各阶段与最终交付的**可判定**验收标准。

## 1. 验收原则

| 原则 | 说明 |
| --- | --- |
| 可判定 | 每条标准可用「是/否」或数值阈值判定 |
| 可复现 | 验收过程本身可重复，不依赖主观印象 |
| 可追溯 | 每条标准对应具体任务与交付物 |
| 分层 | 阶段验收 → 里程碑验收 → 项目终验收 |

## 2. 阶段验收标准

> **状态截至 2026-09-21。** 标记含义：`[x]` 已完成 · `[~]` 部分 · `[ ]` 未达成。各条标记的依据汇总于[合规审计](/zh/plan/audit)，并在仓库根目录 `AUDIT.md` 中逐条给出证据。

### A1 数据管线

**对应**：阶段一 / M1

- [x] **已完成** —— `scripts/build_dataset.py --source raw|synthetic` 单命令产出全部 Parquet
- [~] **部分** —— `data/processed/manifest.json` 只记录行数，无校验和清单与可复现性测试
- [x] **已完成** —— `decoders.py::decode_multi` / `encode_multi`（覆盖 `1SSAATTTTT` 与 `0DDTTTTTMM`），由 `tests/unit/test_decoders.py` 覆盖
- [~] **部分** —— `data/processed/reconciliation.json` 仅有汇总，一致率未做测试断言
- [x] **已完成** —— `data/splits/{train,val,test}_ids.parquet`，并在 `reconciliation.json` 中对账
- [x] **已完成** —— `splits.py::assert_no_leakage`，经 `evaluation/protocol.py` 转发；`features.py` 强制关键字参数 `as_of`
- [~] **部分** —— 已接入 `pytest-cov` 与 `[tool.coverage.run]`，CI 运行 `--cov=wca_bench`；但尚未强制 ≥ 80% 的数值阈值
- [x] **已完成** —— `datacard.md`（英）+ `datacard_zh.md`（中），含允许/禁止用途章节
- [ ] **未达成** —— 无基准脚本、无实测数据

### A2 任务定义

**对应**：阶段二 / M2

- [x] **已完成** —— `docs/tasks/*`：每个页面均含定义、输入输出、指标、基线与领域挑战
- [~] **部分** —— 指标与分层维度已明确；配对单位集中记录于 `docs/evaluation/statistics`，未写入各任务页
- [x] **已完成** —— `configs/task3_dnf_rate.yaml`（`hard_subset.historical_dnf_rate: [0.1, 0.3]`）；`evaluation/stratified.py` 支持硬样本掩码
- [x] **已完成** —— `Report.extras["cold_start"]`，在 `examples/` 报告中可见
- [ ] **未达成** —— 无评审记录、无冻结版本标记

### A3 基线实现

**对应**：阶段二 / M3

- [x] **已完成** —— 21 个基线、每任务 4–5 个（目标为 ≥ 18）；见[任务套件 · 基线清单](/zh/tasks/#_5-基线清单)
- [x] **已完成** —— `.github/workflows/ci.yml` 运行 `run_all_baselines.py --mode small`；`tests/integration/test_end_to_end.py` 遍历任务注册表
- [x] **已完成** —— 每份报告都含 `overall` + 四维分层 + `significance` + `cost`
- [x] **已完成** —— `scripts/build_leaderboard.py` → `examples/leaderboard.{md,csv}`
- [x] **已完成** —— 22 个 `configs/*.yaml` 覆盖全部 21 个基线
- [x] **已完成** —— 种子 42 / 43 / 44 由 `scripts/run_multi_seed.py` 聚合为 `examples/multi_seed.md`，覆盖全部 21 个基线
- [x] **已完成** —— `evaluation/significance.py` 已由任务运行器调用并落盘到每份报告

### A4 发布

**对应**：阶段三 / M4、M5

- [ ] **未达成** —— 外部投稿环节
- [x] **已完成** —— `paper/sections/08_limitations_ethics.tex`
- [x] **已完成** —— `README` / `LICENSE`(Apache-2.0) / `CONTRIBUTING` / `CODE_OF_CONDUCT` / `CITATION.cff`，并附中文版；`CITATION.cff` 占位 URL 已修复
- [x] **已完成** —— `publish/huggingface/`：数据集卡片、`dataset_infos.json`、LFS 属性、dry-run 上传脚本
- [x] **已完成** —— `publish/huggingface/upload_models.py` 将基线报告发布为模型仓库
- [x] **已完成** —— 双语站点（`/` + `/zh/`）构建通过并通过链接/锚点校验；部署由 `docs.yml` 负责
- [x] **已完成** —— `scripts/validate_submission.py`，并在 CI 中对 `examples/submission_template/` 实际执行
- [ ] **未达成** —— 外部事项
- [ ] **未达成** —— 外部事项

### A5 迭代与扩展

**对应**：阶段四 / M6

- [ ] **未达成** —— 尚未收集社区反馈
- [ ] **未达成** —— 无 v1.1、无变更日志
- [ ] **未达成** —— 依赖窗口期之后的数据发布
- [x] **已完成** —— 图（`gnn`）、贝叶斯（`beta_binomial`、`hierarchical_shrinkage`）与因果（`iv_2sls`、`causal_forest`）基线已纳入排行榜
- [ ] **未达成** —— 外部事项
- [ ] **未达成** —— 外部事项
- [ ] **未达成** —— 维护者手册与路线图 v2 尚未撰写

## 3. 最终交付验收

| 编号 | 交付物 | 验收判据 |
| --- | --- | --- |
| D1 | WCA-Bench 数据集 | 可加载、卡片完整、覆盖 17 个现役项目 |
| D2 | 预处理管线与加载器 | 单命令可复现，测试覆盖率达标 |
| D3 | 数据卡 | 含来源/规模/字段/划分/偏差/用途约束 |
| D4 | 五任务定义与评估协议 | 五要素齐全，通过评审并冻结 |
| D5 | 基线实现与结果 | ≥ 18 基线，Report 结构完整 |
| D6 | 排行榜与提交规范 | 可一键重建，提交校验可用 |
| D7 | 主论文 | 已投稿 NeurIPS E&D |
| D8 | 公开代码仓库 | 公开、CI 绿、治理文件齐全 |
| D9 | 挑战赛与结果分析 | 竞赛上线 + 分析报告 |

## 4. 质量门禁（Quality Gates）

每个 PR / 发布必须通过：

```text
Gate 1  Lint & 类型检查通过
Gate 2  单元测试全通过，覆盖率不下降
Gate 3  小样本端到端测试通过
Gate 4  文档站构建成功
Gate 5  无未来信息泄漏断言通过
Gate 6  （发布时）复现等级 ≥ L2，主排行榜 ≥ L3
```

## 5. 判定与豁免

| 情形 | 处理 |
| --- | --- |
| 某项标准因外部原因不可达 | 项目负责人书面记录并调整，纳入变更日志 |
| 破坏性变更导致既有标准失效 | 通过版本化机制另立标准，不追溯旧榜 |
| 指标阈值需要调整 | 需 ≥ 2 人评审并记录理由 |

## 6. 后续阅读

- [风险与缓解 →](/zh/plan/risks)
- [里程碑](/zh/plan/roadmap#_2-关键里程碑)
