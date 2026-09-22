# WCA-Bench 数据卡

> 本数据卡遵循 *Datasheets for Datasets* 规范，是本数据集内容与使用方式的权威说明。
> 英文主版本见 [`datacard.md`](datacard.md)。

## 1. 基本信息

| 字段 | 值 |
| --- | --- |
| 名称 | WCA-Bench |
| 版本 | 0.1.0 |
| 数据来源 | World Cube Association Results Database Export |
| 导出格式 | v2.0.2（snake_case，含 `result_attempts`） |
| 官方说明 | https://www.worldcubeassociation.org/export/results |
| API 元数据 | https://www.worldcubeassociation.org/api/v0/export/public |
| 代码许可证 | Apache-2.0 |
| 数据权利 | World Cube Association |
| 数据卡语言 | 简体中文（英文主版本见 `datacard.md`） |

## 2. 规模

### 2.1 官方导出（约）

| 表 | 规模 |
| --- | --- |
| `persons` | 约 29.8 万 |
| `competitions` | 约 1.87 万 |
| `results` | 约 690 万 |
| `result_attempts` | 按轮次格式逐次记录 |
| `scrambles` | 约 310 万 |
| `events` | 17 个现役项目 + 已废止项目 |

### 2.2 WCA-Bench 发布产物

| 产物 | 说明 |
| --- | --- |
| `data/processed/*.parquet` | 解码并归一化后的数据表 |
| `data/processed/person_event_stats.parquet` | 冻结的选手–项目统计量 |
| `data/processed/frozen_stats.json` | 从训练窗口计算的冻结基准统计量 |
| `data/splits/{train,val,test}_ids.parquet` | 行级划分索引 |
| `data/splits/person_history.parquet` | 按时间排序的选手参赛历史 |
| `data/splits/test_time_slices.json` | Test-A / B / C 的时间边界 |

同时提供小规模**合成导出**（`scripts/generate_synthetic.py`），用于 CI 与离线开发。它由固定种子生成、不含真实个人信息，且**不得**作为基准结果上报。

## 3. 字段语义

- `best` / `average`：该轮最优单次与平均成绩。
- 哨兵值：`-1` = DNF（未完成），`-2` = DNS（未开始），`0` = 无成绩。
- 正数值含义取决于项目 `format`：
  - `time`：百分之一秒（`8653` = 1:26.53）。
  - `number`：步数（最少步数）；存储的 average 为均值的 100 倍。
  - `multi`：多盲复合编码（见下）。
- `333mbf` 打乱：TSV 导出中换行被替换为 `|`，预处理时还原。

### 3.1 多盲编码

多盲成绩使用复合十进制编码：

```text
旧版：1 S S A A T T T T T     （完成数 / 尝试数 / 用时秒）
新版：0 D D T T T T T M M     （差值 / 用时秒 / 未完成数）
```

`wca_bench.data.decoders` 实现了双向编解码，并由单元测试覆盖往返一致性不变量
（`encode(decode(v)) == v`）。

### 3.2 轮次格式归一化

- *best of 3*：三次尝试取最小。
- *average of 5*：去除最优与最差后取算术平均。
- *mean of 3*：三次尝试的算术平均。

重建的 average 会与官方 `results.average` 对账，对账摘要写入
`data/processed/reconciliation.json`。

## 4. 划分

| 集合 | 时间范围 | 用途 |
| --- | --- | --- |
| train | 2003–2022 | 拟合与基准统计量估计 |
| validation | 2023–2024 | 超参调优与模型选择 |
| test | 2025–2026 | 最终评估（固定窗口） |
| Test-A / B / C | 2025H1 / 2025H2 / 2026H1 | 时间鲁棒性子集 |

划分为**时间分割而非随机分割**，主排行榜始终基于固定的 2025–2026 窗口。窗口之后新增的数据作为 *扩展测试集* 单独发布。

## 5. 已知偏差与限制

- **项目覆盖不均。** 三阶在数量上占绝对主导；高盲、多盲等项目的记录远少于三阶。
- **地区不平等。** 各国举办比赛的机会差异显著，限制了跨地区泛化结论。
- **类别不平衡。** 各项目 DNF 率差异很大，使分类指标对阈值选择敏感。
- **非平稳性。** 规则变更、硬件演进与训练方法革新使 23 年的成绩分布非平稳。
- **技能迁移的自选择。** 选手自行决定何时开始新项目，因此朴素相关会系统性高估因果迁移效应。
- **禁止人口属性推断。** 不得用于推断 WCA 已公开字段之外的个人属性。

## 6. 允许用途

- 科研与教学：体育数据分析、基准方法学、可复现评估。
- 社区服务：选手表现分析、比赛组织者的轮次与晋级设计参考。
- 聚合统计分析与方法对比研究。

## 7. 禁止用途

- 赌博、博彩或任何形式的投注预测。
- 对选手个体的歧视性筛选、画像或骚扰。
- 冒充官方机构或伪造赛事结果。
- 在未匿名化的前提下二次分发个体级、隐私敏感的衍生数据。

## 8. 署名要求

再发布任何源自 WCA 导出的信息时，必须包含：

> This information is based on competition results owned and maintained by the
> World Cube Association, published at https://worldcubeassociation.org/results

## 9. 伦理与退出机制

- 选手可联系项目维护者，申请从个体级衍生特征中移除其记录；聚合统计量予以保留。
- 项目承诺遵守 WCA 公开数据使用条款。
- 本基准作为研究产物发布，**不是**排名权威机构，不得以此身份呈现。

## 10. 复现入口

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev,fast,boost]"
python scripts/generate_synthetic.py --small
python scripts/build_dataset.py --source synthetic
python scripts/run_all_baselines.py --mode small
python scripts/build_leaderboard.py
```

真实数据：先执行 `python scripts/download_data.py`，再执行
`python scripts/build_dataset.py --source raw`。
