---
layout: home

hero:
  name: WCA-Bench
  text: 体育数据分析的标准化基准
  tagline: 首个基于世界魔方协会（WCA）全部公开比赛数据的综合性机器学习基准 —— 5 类核心任务、289k 选手、660 万条成绩、严格的防泄漏评估协议
  actions:
    - theme: brand
      text: 阅读项目计划书
      link: /guide/
    - theme: alt
      text: 查看开发计划
      link: /plan/
    - theme: alt
      text: 在 GitHub 上查看
      link: https://github.com/

features:
  - icon: 🎯
    title: 定义一个科学问题
    details: 不追求新模型，而是回答「在体育竞技数据的真实约束下，不同方法论的表现如何」。问题本身即具独立研究价值。
  - icon: 🗄️
    title: 真实而非合成
    details: 数据来自 WCA 官方数据库导出（persons / results / scrambles 等），覆盖 17 个现役项目与 23 年纵向追踪记录。
  - icon: 🧩
    title: 五大任务难度谱
    details: 成绩预测（回归）、名次预测（排序）、DNF 预测（分类）、人类极限估计（极值）、技能迁移（因果推断）。
  - icon: 🔒
    title: 严格防泄漏
    details: 时间分割 + 滚动窗口评估，基准统计量在测试窗口期间冻结，杜绝任何形式的未来信息泄漏。
  - icon: 📊
    title: 分层评估框架
    details: 按项目、选手水平、时间、地区四维分层报告，避免结果被主导群体掩盖。
  - icon: 🔁
    title: 可复现优先
    details: 训练代码、随机种子、预处理脚本、模型权重（HuggingFace）与算力成本全部公开。
---

## 这是什么

WCA-Bench 是 **首个基于世界魔方协会（WCA）全部公开比赛数据的综合性机器学习基准**。它涵盖成绩预测、名次预测、DNF 预测、人类极限估计和技能迁移分析五类核心任务，为体育数据分析领域提供标准化的评估协议与可复现的实验框架。

## 文档导航

| 板块 | 内容 | 入口 |
| --- | --- | --- |
| **项目计划书** | 项目目标、范围、技术方案概述、预期成果 | [进入 →](/guide/) |
| **技术方案** | 数据基础设施、任务套件定义、评估框架 | [进入 →](/data/) |
| **开发计划** | 目录组织、阶段划分、里程碑、任务分解、依赖与验收标准 | [进入 →](/plan/) |

## 快速开始（文档站点）

```bash
npm install          # 安装依赖
npm run docs:dev     # 本地预览（默认 http://localhost:5173）
npm run docs:build   # 构建静态站点到 docs/.vitepress/dist
npm run docs:preview # 预览构建产物
```
