# WCA-Bench
> 基于世界魔方协会（WCA）数据库的体育数据分析标准化基准

WCA-Bench 是首个基于世界魔方协会（WCA）公开比赛数据的综合性机器学习基准，涵盖**成绩预测、名次预测、DNF 预测、人类极限估计、技能迁移分析**五类核心任务，为体育数据分析领域提供标准化的评估协议与可复现的实验框架。

## 核心特征

| 维度 | 说明 |
| --- | --- |
| 数据来源 | WCA 真实比赛数据（导出 v2.0.2：persons / results / result_attempts 等） |
| 任务类型 | 回归、排序、不平衡分类、极值估计、因果推断 |
| 时间维度 | 纵向追踪（选手职业生涯，2003–2026） |
| 领域规则 | 轮次格式（ao5/mo3）、DNF/DNS（-1/-2）、多盲编码 `1SSAATTTTT` / `0DDTTTTTMM` |
| 评估协议 | 时间分割 + 滚动窗口 + 冻结统计量，严格防泄漏 |
| 分层报告 | 项目 / 选手水平 / 时间 / 地区 四维分层 |
| 许可证 | **Apache-2.0**（代码）；数据版权归 WCA |

## 快速开始

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate    # macOS / Linux
pip install -e ".[dev,fast,boost]"

# 离线合成数据端到端（CI / 演示）
python scripts/generate_synthetic.py --small
python scripts/build_dataset.py --source synthetic
python scripts/run_all_baselines.py --mode small
python scripts/build_leaderboard.py
pytest
```

真实 WCA 数据：

```bash
python scripts/download_data.py
python scripts/build_dataset.py --source raw
python scripts/run_all_baselines.py --mode full
```

## 文档

本项目使用 **VitePress** 管理文档，文档源码位于 `docs/`。

```bash
npm install
npm run docs:dev
npm run docs:build
```

| 层级 | 目录 | 面向读者 |
| --- | --- | --- |
| 项目计划书 | `docs/guide/` | 决策者、审阅者 |
| 技术方案 | `docs/data/`、`docs/tasks/`、`docs/evaluation/` | 方法研究者、实现者 |
| 开发计划 | `docs/plan/` | 执行者、贡献者 |

建议先读 `docs/guide/index.md`（执行摘要），再读 `docs/plan/index.md`（开发计划总览）。

## 仓库结构

```text
wca-bench/
├── docs/                    # VitePress 文档
├── src/wca_bench/           # Python 主包
│   ├── data/                # 加载、解码、特征、时间分割、合成数据
│   ├── tasks/               # T1–T5 任务适配
│   ├── baselines/           # 统计 / 树模型 / 因果等基线
│   ├── evaluation/          # 指标、滚动协议、分层、显著性
│   └── leaderboard/         # 排行榜聚合
├── configs/                 # 实验配置
├── scripts/                 # 下载 / 构建 / 基线 / 排行榜
├── tests/                   # 单元与集成测试
├── datacard.md              # 数据卡
├── LICENSE                  # Apache-2.0
└── pyproject.toml
```

## 五任务速览

| ID | 任务 | 主指标 |
| --- | --- | --- |
| T1 | 成绩预测 | MAE/RMSE（log） |
| T2 | 名次预测 | Kendall's τ、前3重叠、Brier |
| T3 | DNF 预测 | AUC-PR、MCC、校准 |
| T4 | 人类极限估计 | 留一稳定性、与领域知识一致性 |
| T5 | 技能迁移 | 迁移矩阵 + 稳健性 |

## 示例结果（真实 WCA 导出）

已在官方导出 v2.0.2（约 691 万条 results）上完成数据管线与五任务基线抽样评估，结果见 [`examples/leaderboard.md`](examples/leaderboard.md)。

| 任务 | 最佳基线（抽样） | 主指标 |
| --- | --- | --- |
| T1 成绩预测 | xgboost_log | MAE(log) = 0.191 |
| T2 名次预测 | psych_sheet / PL | Kendall τ = 0.767 |
| T3 DNF 预测 | historical_dnf_rate | AUC-PR = 0.389 |
| T4 极限估计 | exponential_decay | 事件级极限估计 |
| T5 技能迁移 | spearman | 423 个可识别项目对 |

## 许可证与数据署名

- 代码以 **Apache License 2.0** 发布（见 `LICENSE`）。
- 数据版权归 World Cube Association 所有；再发布时请遵守官方导出条款并保留署名：
  > This information is based on competition results owned and maintained by the World Cube Association, published at https://worldcubeassociation.org/results
- 使用约束见 [`datacard.md`](datacard.md)。
