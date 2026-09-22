# WCA-Bench Submission Template

这是排行榜提交的最小骨架，用于展示 `docs/evaluation/reproducibility.md`
「排行榜提交格式」要求的目录结构与占位内容。

## 文件清单

| 文件 | 说明 |
| --- | --- |
| `report/` | 评估报告集合，含 overall 与四维分层、校准、显著性、成本 |
| `predictions.parquet` | 每场比赛的原始预测（键列 + 预测列） |
| `config.yaml` | 模型与训练配置 |
| `environment.yml` | 环境锁定 |
| `seeds.json` | 随机种子列表 |
| `cost.json` | 算力报告 |
| `README.md` | 复现步骤 |

## 校验

```bash
python scripts/validate_submission.py examples/submission_template
```

退出码为 0 表示通过。提交真实结果时请用完整的预测数据替换占位内容。
