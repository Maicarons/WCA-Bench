# 目录组织与文档分层

本章定义 WCA-Bench 在 GitHub 上的完整项目结构，包括代码模块职责与文档分层体系。

## 1. 完整仓库结构（目标态）

```text
wca-bench/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                # 单元测试 + 小样本端到端
│   │   ├── docs.yml              # VitePress 文档构建与部署
│   │   └── lint.yml             # 代码风格与类型检查
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── PULL_REQUEST_TEMPLATE.md
│
├── data/                         # 数据产物（不入库，见 .gitignore）
│   ├── raw/                      # 原始 WCA 导出文件
│   ├── processed/                # 预处理后的 Parquet 文件
│   └── splits/                   # 时间分割的 train/val/test 索引
│
├── src/wca_bench/                # 主 Python 包
│   ├── data/
│   │   ├── loader.py             # 数据加载与预处理
│   │   ├── decoders.py           # 多盲编码、成绩值解码
│   │   ├── features.py           # 特征工程
│   │   ├── splits.py             # 时间分割与冻结统计量
│   │   └── schema.py             # 表结构与类型定义
│   ├── tasks/
│   │   ├── base.py               # 统一 Task 接口
│   │   ├── result_prediction/    # 任务一
│   │   ├── placement/            # 任务二
│   │   ├── dnf/                  # 任务三
│   │   ├── limit/                # 任务四
│   │   └── transfer/             # 任务五
│   ├── baselines/                # 基线模型实现
│   │   ├── statistical/          # 统计基线（KDE、Plackett-Luce）
│   │   ├── tree/                 # 树模型（RF、XGBoost、LightGBM）
│   │   ├── deep/                 # 深度学习（LSTM、Transformer）
│   │   ├── graph/                # 图学习（GNN）
│   │   ├── bayesian/             # 贝叶斯（PyMC / NumPyro）
│   │   └── causal/               # 因果（DID、IV、因果森林）
│   ├── evaluation/               # 评估指标与协议
│   │   ├── metrics.py            # 指标实现
│   │   ├── protocol.py           # 滚动窗口协议
│   │   ├── stratified.py         # 分层评估
│   │   └── significance.py       # 统计检验与效应量
│   ├── leaderboard/              # 排行榜与提交校验
│   └── utils/                    # 通用工具（种子、日志、IO）
│
├── configs/                      # 实验配置文件
│   ├── task1_*.yaml
│   ├── task2_*.yaml
│   └── ...
│
├── notebooks/                    # 探索性分析
│   ├── 01_data_exploration.ipynb
│   ├── 02_domain_rules.ipynb
│   └── 03_baseline_analysis.ipynb
│
├── tests/                        # 单元测试与集成测试
│   ├── unit/
│   └── integration/
│
├── docs/                         # 文档（VitePress 站点）
│   ├── .vitepress/
│   │   ├── config.mts
│   │   └── theme/
│   ├── index.md
│   ├── guide/                    # 项目计划书
│   ├── data/                     # 数据基础设施
│   ├── tasks/                    # 任务套件
│   ├── evaluation/               # 评估框架
│   └── plan/                     # 开发计划
│
├── scripts/                      # 自动化脚本
│   ├── download_data.sh          # 下载 WCA 导出
│   ├── build_dataset.py          # 一键构建数据集
│   ├── run_all_baselines.py      # 运行全部基线
│   └── build_leaderboard.py      # 生成排行榜
│
├── datacard.md                   # 数据卡（Data Card）
├── CONTRIBUTING.md               # 贡献指南
├── CODE_OF_CONDUCT.md            # 行为准则
├── LICENSE                       # Apache-2.0 许可证
├── README.md                     # 项目主页
├── CITATION.cff                  # 引用信息
├── pyproject.toml                # Python 包配置
└── package.json                  # 文档工程配置（VitePress 脚本与依赖）
```

## 2. 模块职责

| 模块 | 职责 | 不负责 |
| --- | --- | --- |
| `src/wca_bench/data` | 加载、解码、特征、分割 | 模型与评估逻辑 |
| `src/wca_bench/tasks` | 任务定义与适配 | 具体模型实现 |
| `src/wca_bench/baselines` | 模型实现（可替换） | 评估协议 |
| `src/wca_bench/evaluation` | 指标、协议、分层、检验 | 数据加载 |
| `src/wca_bench/leaderboard` | 提交校验与排名 | 模型训练 |
| `scripts` | 编排与自动化 | 核心算法 |

**依赖方向（单向）：**

```text
tasks ──► data
baselines ──► tasks ──► data
evaluation ──► tasks + data
leaderboard ──► evaluation
```

禁止反向依赖（如 `data` 不得 import `tasks`），以 `tests/unit/test_import_policy.py` 强制校验。

## 3. 文档分层体系

文档按**读者意图**分层，三层递进：

```text
第一层：项目计划书（guide/）      —— 给决策者/审阅者
    目标 · 范围 · 方案概述 · 预期成果

第二层：技术方案（data / tasks / evaluation）
    —— 给方法研究者/实现者
    数据契约 · 任务定义 · 评估协议

第三层：开发计划（plan/）         —— 给执行者/贡献者
    目录结构 · 阶段任务 · 依赖 · 验收 · 风险
```

### 3.1 文档清单

| 层级 | 目录 | 页面 |
| --- | --- | --- |
| 计划书 | `docs/guide/` | 执行摘要、项目概述、范围、技术方案概述、预期成果 |
| 数据 | `docs/data/` | 总览、数据来源、预处理、划分 |
| 任务 | `docs/tasks/` | 总览 + 五任务 |
| 评估 | `docs/evaluation/` | 总览、协议、统计、复现性 |
| 开发 | `docs/plan/` | 总览、结构、路线图、四阶段、依赖、验收、风险、发表 |

### 3.2 文档维护约定

- 每个代码模块在 `docs/` 中有对应页面
- PR 修改任务定义/评估协议时**必须同步更新文档**
- 文档站点通过 GitHub Actions 自动部署（`docs.yml`）
- 文档与代码同仓库、同版本发布

## 4. 命名与规范

| 类型 | 规范 | 示例 |
| --- | --- | --- |
| Python 模块 | 蛇形命名 | `result_prediction` |
| 类 | 大驼峰 | `ResultPredictionTask` |
| 配置 | `task<编号>_<模型>.yaml` | `task1_kde.yaml` |
| 分支 | `<type>/<scope>-<desc>` | `feat/dnf-xgboost` |
| 提交 | Conventional Commits | `feat(dnf): 添加 XGBoost 基线` |
| Issue | `<type>: <简述>` | `bug: 多盲解码边界错误` |

## 5. 后续阅读

- [阶段划分与里程碑 →](/plan/roadmap)
- [依赖关系 →](/plan/dependencies)
