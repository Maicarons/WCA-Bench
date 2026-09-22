# 目录组织与文档分层

本章定义 WCA-Bench 的项目结构：**当前实际布局**（§1）、与计划中目标布局的差异（§2）、模块职责（§3）、文档分层体系（§4）、命名规范（§5）以及构建说明（§6）。

## 1. 当前实际仓库结构

下面的目录树反映 **2026-09-21 审计快照**时的仓库状态（见[合规审计](/zh/plan/audit)）。

```text
wca-bench/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                     # 单元测试（含覆盖率）、合成小样本端到端、提交模板校验
│   │   ├── docs.yml                   # VitePress 构建与部署
│   │   └── lint.yml                   # ruff
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── PULL_REQUEST_TEMPLATE.md
│
├── configs/                           # 22 个实验配置（21 个基线 + default.yaml）
│
├── data/                              # 生成产物，不入库（见 .gitignore）
│   ├── raw/                           # WCA TSV 导出（v2.0.2）+ metadata.json
│   ├── processed/                     # Parquet 表 + manifest.json + reconciliation.json
│   └── splits/                        # {train,val,test}_ids.parquet、person_history.parquet、
│                                      # person_event_stats.parquet、test_time_slices.json、frozen_stats.json
│
├── docs/                              # VitePress 文档站点（英文为根语言）
│   ├── .vitepress/
│   │   ├── config.mts                 # locales：root（en-US）+ zh（zh-CN）
│   │   └── theme/                     # 默认主题 + custom.css
│   ├── index.md
│   ├── guide/                         # 项目计划书（5 页）
│   ├── data/                          # 数据基础设施（4 页）
│   ├── tasks/                         # 任务套件（6 页）
│   ├── evaluation/                    # 评估框架（5 页，含计算与硬件）
│   ├── plan/                          # 开发计划（12 页，含合规审计）
│   └── zh/                            # 简体中文 locale —— 与上述五大板块一一对应
│
├── examples/                          # 抽样测试集上的基线报告
│   ├── README.md
│   ├── leaderboard.md
│   ├── leaderboard.csv
│   ├── leaderboard.json
│   ├── multi_seed.md                  # 主指标在种子 42 / 43 / 44 上的均值 ± 标准差
│   ├── result_prediction__*.json      # T1 × 5：xgboost_log、history_mean、kde、ridge_log、lstm
│   ├── placement__*.json              # T2 × 4：psych_sheet、plackett_luce、kde_simulation、gnn
│   ├── dnf__*.json                    # T3 × 4：xgboost_dnf、beta_binomial、historical_dnf_rate、logistic
│   ├── limit__*.json                  # T4 × 4：exponential_decay、changepoint、gp_evt、hierarchical_shrinkage
│   ├── transfer__*.json               # T5 × 4：spearman_correlation、did_proxy、iv_2sls、causal_forest
│   └── submission_template/           # 排行榜提交骨架
│       ├── README.md
│       ├── config.yaml
│       ├── environment.yml
│       ├── seeds.json
│       ├── cost.json
│       ├── predictions.parquet
│       └── report/                    # overall、by_event、by_skill_level、by_time_slice、
│                                      # by_continent、calibration、significance、cost
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_domain_rules.ipynb
│   └── 03_baseline_analysis.ipynb
│
├── paper/                             # 可直接投稿 arXiv 的 XeLaTeX 论文
│   ├── main.tex
│   ├── preamble.tex
│   ├── references.bib
│   ├── main.pdf
│   ├── Makefile
│   ├── .latexmkrc
│   ├── README.md
│   ├── check_bib.py
│   ├── sections/                      # 00_abstract … 10_appendix（11 个文件）
│   └── figures/                       # fig1_task_overview.pdf … fig4_transfer_pairs.pdf + make_figures.py
│
├── publish/                           # 数据集/模型发布材料（已就绪，尚未实际上传）
│   ├── README.md
│   ├── DATASET_LAYOUT.md
│   ├── huggingface/
│   │   ├── README.md                  # 数据集卡片（英文，含 YAML front matter）
│   │   ├── .gitattributes             # Git LFS 规则
│   │   ├── dataset_infos.json
│   │   ├── upload_dataset.py
│   │   ├── upload_models.py
│   │   └── requirements.txt
│   ├── modelscope/
│   │   ├── README.md                  # 数据集卡片（英文 + 中文摘要）
│   │   ├── configuration.json
│   │   ├── dataset_meta.json
│   │   ├── upload.py
│   │   └── requirements.txt
│   ├── tools/
│   │   ├── stage_release.py           # 汇总 data/processed + data/splits + examples
│   │   └── make_archive.py            # tar.gz / zip 归档 + SHA256 清单
│   └── _staging/                      # 由 stage_release.py 生成
│       └── dataset/                   # data/、examples/、dataset_infos.json、RELEASE_MANIFEST.json
│
├── scripts/                           # 8 个可执行脚本 —— 见 §1.1
│
├── src/wca_bench/                     # Python 包
│   ├── data/
│   │   ├── loader.py                  # 数据加载与预处理
│   │   ├── decoders.py                # 成绩值、多盲编码、打乱序列规范化
│   │   ├── features.py                # 特征工程（强制关键字参数 `as_of`）
│   │   ├── splits.py                  # 时间分割、冻结统计量、`assert_no_leakage`
│   │   ├── schema.py                  # 表结构与类型定义
│   │   └── synthetic.py               # 离线 / CI 用合成数据生成器
│   ├── tasks/
│   │   ├── base.py                    # 统一 `Task` 协议 + `BaseTask`
│   │   ├── result_prediction/         # T1
│   │   ├── placement/                 # T2
│   │   ├── dnf/                       # T3
│   │   ├── limit/                     # T4
│   │   └── transfer/                  # T5
│   ├── baselines/
│   │   ├── statistical/               # history_mean、kde、kde_placement、plackett_luce、
│   │   │                              # dnf_rate、world_record、gp_evt_limit
│   │   ├── tree/                      # ridge_result、xgb_result、logistic_dnf、xgb_dnf
│   │   ├── bayesian/                  # beta_binomial_dnf、hierarchical_limit
│   │   ├── deep/                      # lstm_result
│   │   ├── graph/                     # gnn_placement
│   │   └── causal/                    # did、iv、causal_forest
│   ├── evaluation/
│   │   ├── metrics.py                 # 指标实现
│   │   ├── protocol.py                # 滚动窗口协议
│   │   ├── stratified.py              # 四维分层评估
│   │   └── significance.py            # 配对检验、Bootstrap CI、Friedman/Nemenyi、效应量
│   ├── leaderboard/
│   │   └── builder.py                 # 排行榜聚合与主指标定义
│   ├── utils/
│   │   ├── device.py                  # CPU 优先的设备解析（`cpu` / `auto` / `cuda`）
│   │   ├── io.py                      # JSON / Parquet 读写辅助
│   │   ├── logging.py
│   │   └── seed.py                    # 可复现随机种子
│   └── py.typed
│
├── tests/
│   ├── unit/                          # 解码、分割、指标、显著性、新基线、
│   │                                  # 导入策略、提交校验
│   └── integration/                   # 端到端（合成小样本）
│
├── AUDIT.md                           # 对照本计划的合规审计（完整版）
├── CITATION.cff
├── CODE_OF_CONDUCT.md / CODE_OF_CONDUCT_zh.md
├── CONTRIBUTING.md / CONTRIBUTING_zh.md
├── LICENSE                            # Apache-2.0
├── README.md / README_zh.md
├── datacard.md / datacard_zh.md
├── package.json / package-lock.json   # 文档工具链（VitePress）
├── pyproject.toml
└── plan.md                            # 用户提供的原始项目计划书（见 AUDIT.md H4）
```

### 1.1 脚本清单

| 脚本 | 用途 |
| --- | --- |
| `build_dataset.py` | 一键构建：`--source raw\|synthetic` → `data/processed/` + `data/splits/` |
| `download_data.py` | 下载官方 WCA TSV 导出 |
| `download_data.sh` | 下载步骤的便捷封装 |
| `generate_synthetic.py` | 离线 / CI 用合成数据集（`--small`） |
| `run_all_baselines.py` | 运行已注册基线（`--mode small\|full`） |
| `run_multi_seed.py` | 跨种子聚合主指标（均值 ± 标准差），输出 `outputs/multi_seed/multi_seed.json` 与 `examples/multi_seed.md` |
| `build_leaderboard.py` | 聚合报告为 `examples/leaderboard.{md,csv}` |
| `validate_submission.py` | 按排行榜提交规范校验提交目录 |

> 早期的临时调试脚本（`_debug_*.py`、`_run_limit_transfer.py`、`_run_remaining.py`）已被删除，仓库中不应再引用它们。

## 2. 目标布局与差异

计划最初设计的是一个更精简的仓库。下表记录现实已超出原目标的部分，以及目标中仍未达成的部分。

```text
目标骨架（来自最初计划）
wca-bench/
├── .github/workflows/            ci.yml · docs.yml · lint.yml
├── data/                         raw · processed · splits
├── src/wca_bench/                data · tasks · baselines · evaluation · leaderboard · utils
├── configs/                      task<编号>_<模型>.yaml
├── notebooks/                    01_data_exploration · 02_domain_rules · 03_baseline_analysis
├── tests/                        unit · integration
├── docs/                         guide · data · tasks · evaluation · plan
├── scripts/                      download · build · baselines · leaderboard
└── datacard.md · CONTRIBUTING.md · CODE_OF_CONDUCT.md · LICENSE · README.md ·
    CITATION.cff · pyproject.toml · package.json
```

| 目标项 | 当前仓库状态 |
| --- | --- |
| `src/wca_bench/` 布局 | **已达成** —— 六个子包全部填充，含 `deep/`、`graph/`、`bayesian/` |
| `notebooks/01…03` | **已达成** —— 三个可执行 notebook（原为单个 `00_readme.py`） |
| `configs/*.yaml` | **已达成并扩展** —— 22 个配置覆盖全部 21 个基线 |
| 治理文件 | **已达成** —— 并额外提供中文版（`README_zh.md`、`datacard_zh.md`、`CONTRIBUTING_zh.md`、`CODE_OF_CONDUCT_zh.md`） |
| `docs/` | **已扩展** —— 英文根语言 + 完整 `docs/zh/` 中文 locale |
| `docs/zh/` | **新增** —— 原计划中不存在 |
| `publish/` | **新增** —— HuggingFace + ModelScope 发布材料与暂存工具 |
| `paper/` | **新增** —— arXiv 可投稿 XeLaTeX 论文，含图表与参考文献检查脚本 |
| `AUDIT.md` | **新增** —— 对照本计划的合规审计 |
| `scripts/` | **已重组** —— 8 个脚本取代原 4 个；`download_data` 拆为 `.py` + `.sh`；新增多种子与提交校验脚本 |
| 流式数据加载器（`P1-T9`） | **仍待完成** —— 已有 `WCABenchData` / `load_dataset`，但无专用流式加载器 |
| Parquet 性能基准（`A1.9`） | **仍待完成** —— 无基准脚本、无实测数据 |

## 3. 模块职责

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

## 4. 文档分层体系

文档按**读者意图**分层，三层递进：

```text
第一层：项目计划书（guide/）      —— 给决策者/审阅者
    目标 · 范围 · 方案概述 · 预期成果

第二层：技术方案（data / tasks / evaluation）
    —— 给方法研究者/实现者
    数据契约 · 任务定义 · 评估协议

第三层：开发计划（plan/）         —— 给执行者/贡献者
    目录结构 · 阶段任务 · 依赖 · 验收 · 风险 · 审计
```

### 4.1 文档清单

| 层级 | 目录 | 页面 |
| --- | --- | --- |
| 计划书 | `docs/guide/` | 执行摘要、项目概述、范围、技术方案概述、预期成果 |
| 数据 | `docs/data/` | 总览、数据来源、预处理、划分 |
| 任务 | `docs/tasks/` | 总览 + 五任务 |
| 评估 | `docs/evaluation/` | 总览、协议、统计、复现性、计算与硬件 |
| 开发 | `docs/plan/` | 总览、结构、路线图、四阶段、依赖、验收、风险、发表、审计 |

### 4.2 文档维护约定

- 每个代码模块在 `docs/` 中有对应页面
- 修改任务定义/评估协议时**必须同步更新文档**
- **两种语言必须保持同步**：改动 `docs/` 下的页面需同步改动 `docs/zh/` 下的对应页面（反之亦然）
- 文档站点通过 GitHub Actions 自动部署（`docs.yml`）
- 文档与代码同仓库、同版本发布

## 5. 命名与规范

| 类型 | 规范 | 示例 |
| --- | --- | --- |
| Python 模块 | 蛇形命名 | `result_prediction` |
| 类 | 大驼峰 | `ResultPredictionTask` |
| 配置 | `task<编号>_<模型>.yaml` | `task1_kde.yaml` |
| 分支 | `<type>/<scope>-<desc>` | `feat/dnf-xgboost` |
| 提交 | Conventional Commits | `feat(dnf): 添加 XGBoost 基线` |
| Issue | `<type>: <简述>` | `bug: 多盲解码边界错误` |

## 6. 构建说明

### 6.1 文档站点

```bash
npm install            # 安装 VitePress 工具链
npm run docs:dev       # 本地预览，默认 http://localhost:5173
npm run docs:build     # 构建静态站点到 docs/.vitepress/dist
npm run docs:preview   # 预览构建产物
```

### 6.2 Windows：`vitepress build` 的盘符大小写陷阱

在 Windows 上，`vitepress build docs` 会依据当前工作目录解析 `srcDir`。若 shell 的工作目录使用**小写盘符**（例如 `f:\workspace\WCA-Bench`），`path.resolve()` 会得到 `f:/...`，而 Rollup 记录的页面 chunk id 使用**真实文件系统大小写** `F:/...`。VitePress 以字符串精确相等来匹配这些绝对路径，因此**所有**页面都匹配不到自己的 chunk，构建中断并报：

```text
TypeError: Cannot read properties of undefined (reading 'imports')
    at resolvePageImports (...)
```

**已修复方案：** `docs/.vitepress/config.mts` 显式设置 `srcDir`，并把 Windows 盘符统一为大写，使两种路径形式一致。该做法不硬编码任何绝对路径，配置保持可移植。

### 6.3 构建目录被占用

若 `docs:dev` 服务仍在运行，VitePress 无法清空 `docs/.vitepress/dist`，构建会在 `emptyDir` 阶段失败。请先停止 dev 服务，或在重新构建前删除 `docs/.vitepress/dist` 与 `docs/.vitepress/cache`。

## 7. 后续阅读

- [合规审计 →](/zh/plan/audit)
- [阶段划分与里程碑 →](/zh/plan/roadmap)
- [依赖关系 →](/zh/plan/dependencies)
