# WCA-Bench Data Card

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

## 2. 规模（真实导出约）

| 表 | 规模 |
| --- | --- |
| persons | ~289k |
| competitions | ~17.7k |
| results | ~6.6M |
| result_attempts | 与 results 轮次格式相关 |
| scrambles | ~3.1M |
| events | 17 现役 + 历史废止项目 |

本仓库同时提供**合成样例数据**（`scripts/generate_synthetic.py`），用于 CI 与离线开发，规模远小于真实导出。

## 3. 字段语义摘要

- `best` / `average`：该轮最优单次与平均成绩
- 特殊值：`-1` DNF，`-2` DNS，`0` 无成绩
- 正数值含义取决于项目 format：
  - `time`：百分之一秒（8653 = 1:26.53）
  - `number`：最少步数；average 存为 100×均值
  - `multi`：多盲复合编码（见官方文档 / `wca_bench.data.decoders`）
- `333mbf` 打乱：TSV 中换行替换为 `|`

## 4. 时间划分

| 集合 | 时间范围 |
| --- | --- |
| train | 2003–2022 |
| val | 2023–2024 |
| test（固定窗口） | 2025–2026 |
| Test-A/B/C | 2025H1 / 2025H2 / 2026H1 |

主排行榜基于固定测试窗口；后续新增数据作为 Extended Test Set 单独报告。

## 5. 已知偏差与限制

- 项目数据量极不均衡（三阶最多，高盲/多盲较少）
- 地区参赛机会不均衡，影响跨地区泛化结论
- DNF 率项目间差异大，分类任务类别不平衡
- 历史规则与设备变迁导致成绩分布非平稳
- 技能迁移估计存在自选择偏差，简单相关会高估因果效应

## 6. 允许用途

- 科研与教学：体育数据分析、基准方法学、可复现实验
- 社区服务：选手表现分析、比赛组织者轮次设置参考
- 聚合统计与方法对比研究

## 7. 禁止用途

- 赌博、博彩或任何形式的投注预测
- 对选手个体的歧视性筛选、画像或羞辱
- 冒充官方机构或伪造赛事结果
- 在未匿名化的前提下二次分发个体级隐私敏感衍生数据

## 8. 署名要求

再发布基于 WCA 导出的信息时，须包含：

> This information is based on competition results owned and maintained by the
> World Cube Association, published at https://worldcubeassociation.org/results

## 9. 伦理与退出机制

- 选手可联系项目维护者申请从个体级衍生特征中移除个人记录（保留聚合统计）
- 项目承诺遵守 WCA 公开数据使用条款

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

真实数据：`python scripts/download_data.py` 后 `python scripts/build_dataset.py --source raw`。
