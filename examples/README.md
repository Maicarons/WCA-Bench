# WCA-Bench 示例结果（真实 WCA 导出 v2.0.2）

本目录收录基于**官方 WCA Results Export**（导出日期 2026-09-21，格式 v2.0.2）在抽样测试集上跑通的基线结果。

## 数据规模（全量构建产物）

| 指标 | 数值 |
| --- | --- |
| results | 6,909,454 |
| persons | 298,551 |
| competitions | 18,708 |
| train / val / test | 3,211,294 / 1,978,851 / 1,719,290 |
| 全局 DNF 率 | 3.18% |
| 冻结 person-event 统计 | 612,224 |

## 抽样评估说明

`scripts/run_all_baselines.py --mode small` 会在测试窗口内随机抽取若干场比赛，并对训练集做代表性抽样，以便在单机上快速完成基线对比。完整排行榜应在全量数据与滚动窗口协议下重跑。

## 排行榜摘要

见 [leaderboard.md](leaderboard.md)。

当前主指标（抽样测试集）：

| 任务 | 最佳基线 | 主指标 | 值 |
| --- | --- | --- | --- |
| T1 成绩预测 | xgboost_log | MAE(log) ↓ | 0.191 |
| T2 名次预测 | psych_sheet / plackett_luce | Kendall τ ↑ | 0.767 |
| T3 DNF 预测 | historical_dnf_rate | AUC-PR ↑ | 0.389 |
| T4 极限估计 | exponential_decay | 已产出事件级极限估计 | — |
| T5 技能迁移 | spearman_correlation | 可识别项目对 | 423 |

## 复现

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev,fast,boost]"

python scripts/download_data.py          # 下载官方 TSV 导出
python scripts/build_dataset.py --source raw
python scripts/run_all_baselines.py --mode small
python scripts/build_leaderboard.py
```

离线/CI 可用合成数据：

```bash
python scripts/generate_synthetic.py --small
python scripts/build_dataset.py --source synthetic
python scripts/run_all_baselines.py --mode small
```
