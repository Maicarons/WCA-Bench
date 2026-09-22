# 发表策略

## 1. 首篇论文目标

**NeurIPS 2026 Evaluations & Datasets Track。**

NeurIPS E&D Track 明确欢迎：

- 「引入数据集并清晰解释其范围、假设、限制，以及如何支持或塑造 AI/ML 生命周期中的评估主张」的投稿
- 「在新的或现有数据集上的基准测试、基准测试工具和方法论」

WCA-Bench **完美契合**这一范围。

## 2. 论文核心贡献声明

1. 提出**首个基于 WCA 真实比赛数据的体育数据分析标准化基准**
2. 定义了**五个具有领域特定挑战的评估任务**
3. 提供了**严格的防泄漏评估协议和分层评估框架**
4. 发布了**完整的基线实现和可复现的实验代码**

## 3. 论文结构建议

| 章节 | 要点 |
| --- | --- |
| Introduction | 研究碎片化与标准化缺失的问题陈述 |
| Related Work | CubeBench 系列、体育数据分析、时间序列基准 |
| The WCA-Bench Dataset | 数据来源、规模、规则解码、划分、数据卡摘要 |
| Tasks | 五任务定义、指标、领域挑战 |
| Evaluation Protocol | 滚动窗口、冻结统计量、四维分层、统计检验 |
| Baselines & Results | ≥ 18 基线、排行榜、分层结果 |
| Discussion | 方法学洞察、性能–成本权衡、饱和分析 |
| Limitations | 外推风险、数据偏差、地区不平衡 |
| Ethics & Broader Impact | 允许/禁止用途、隐私考量 |

## 4. 后续发表路线图

### 第二篇（应用导向）

- **内容**：在 WCA-Bench 上系统评估传统统计方法与深度学习方法的性能差异
- **目标期刊**：*Journal of Quantitative Analysis in Sports* 或 *Machine Learning*

### 第三篇（方法论）

- **内容**：基于 WCA-Bench 中技能迁移任务的挑战，提出新的因果推断方法
- **目标会议**：KDD 或 ICDM

### 第四篇（领域综述）

- **内容**：基于 WCA-Bench 的实验结果，撰写体育数据分析中「规则约束下的预测」综述
- **目标期刊**：*ACM Computing Surveys*

## 5. 发表与发布时序

```text
第 7 月   NeurIPS 投稿（M4）
   │
第 9 月   公开发布（M5）：GitHub + HuggingFace + 文档站点
   │
第 10-12 月  挑战赛 + 期刊扩展规划（M6）
   │
次年      第二篇（应用）→ 第三篇（方法）→ 第四篇（综述）
```

## 6. 学术诚信与合规

| 事项 | 约定 |
| --- | --- |
| 数据许可 | 遵守 WCA 公开数据使用条款 |
| 伦理声明 | 论文含 Ethics / Broader Impact 章节 |
| 复现材料 | 投稿同步提交复现材料（附录 + 匿名仓库） |
| 双盲要求 | 匿名化仓库链接按会议规则处理 |
| 贡献声明 | 使用 CRediT 贡献者角色分类法 |

## 7. 作者与贡献

建议采用 **CRediT** 分类明确贡献：

| 角色 | 说明 |
| --- | --- |
| Conceptualization | 项目定位与任务设计 |
| Data Curation | 数据获取、解码与划分 |
| Methodology | 评估协议与统计方法 |
| Software | 管线、基线与排行榜实现 |
| Writing – Original Draft | 论文主笔 |
| Writing – Review & Editing | 全体作者 |

## 8. 后续阅读

- [里程碑 · M4 / M5 →](/zh/plan/roadmap#_2-关键里程碑)
- [复现性要求 →](/zh/evaluation/reproducibility)
