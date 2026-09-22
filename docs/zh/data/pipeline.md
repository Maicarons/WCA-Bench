# 预处理管线

WCA-Bench 的数据预处理需要处理四类领域特定问题：成绩值解码、打乱序列处理、轮次格式归一化、时间泄漏防护。

## 1. 成绩值解码

正数值的含义**取决于项目的 format 字段**：

| format | 数值含义 | 示例 |
| --- | --- | --- |
| `time` | 百分之一秒 | `8653` → 1 分 26.53 秒 |
| `number` | 原始数字（仅最少步数） | `28` → 28 步 |
| `multi` | 多盲编码 | 需按 `1SSAATTTTT` / `0DDTTTTTMM` 解码 |

特殊值：

| 值 | 含义 | 处理方式 |
| --- | --- | --- |
| `-1` | DNF | 标记为失败，参与 DNF 率统计，不参与均值 |
| `-2` | DNS | 标记为未开始，通常从训练中剔除 |
| `0` | 无成绩 | 视为缺失 |

### 1.1 多盲解码实现要点

```python
def decode_multi(value: int) -> tuple[int, int, int]:
    """将多盲编码解码为 (完成数, 尝试数, 用时秒)。"""
    s = str(value).zfill(10)
    if s[0] == "1":                     # 旧版 1SSAATTTTT
        dd = 99 - int(s[1:3])
        mm = int(s[3:5])
        solved = dd + mm
        attempted = solved + mm
        seconds = int(s[5:10])
    else:                               # 新版 0DDTTTTTMM
        dd = int(s[1:3])
        seconds = int(s[3:8])
        mm = int(s[8:10])
        solved = 99 - dd - mm
        attempted = solved + mm
    return solved, attempted, seconds
```

## 2. 打乱序列处理

`333mbf` 项目的打乱由**多个换行分隔的 3x3 打乱**组成。在 TSV 版本中，换行被替换为 `|` 字符。

预处理步骤：

1. 按 `|` 切分
2. 还原为多行打乱序列
3. 规范化空白字符与转义
4. 校验打乱长度与项目匹配

## 3. 轮次格式归一化

不同轮次格式对结果计算方式不同：

| 格式 | 计算方式 |
| --- | --- |
| best of 3 | 取 3 次中最优 |
| average of 5 | 去除最优与最差尝试后取剩余 3 次算术平均 |
| mean of 3 | 3 次算术平均 |

::: warning 去极值机制的影响
在 ao5 中，**单次 DNF 对最终成绩的影响被放大**（DNF 通常占据「最差」位置而被去除，但若出现两次 DNF 则整轮 DNF）。模型需要显式建模这种规则效应，而不是简单地把尝试值平均。
:::

管线需：

1. 从 `result_attempts` 重建每轮的尝试序列
2. 按 `format_id` 计算标准化的 `average`
3. 与官方 `results.average` 做一致性校验（不一致则记录告警）

## 4. 时间泄漏防护

评估协议必须确保基准计算**仅使用决策时刻可用的信息**：

```text
对于比赛 t 的成绩预测：
    允许：所有 competition_date < date(t) 的数据
    禁止：比赛 t 及其之后的一切数据
    冻结：选手历史均值、世界纪录等基准统计量
```

实现约定：

- 所有特征函数签名强制传入 `as_of` 时间戳
- 特征缓存按 `as_of` 分桶，避免跨时间复用
- 提供断言工具 `assert_no_leakage(features, target_date)` 用于测试

## 5. 管线阶段

```text
Stage 0  原始文件校验（存在性、列头、编码）
   │
Stage 1  全表加载（Polars scan_tsv）
   │
Stage 2  成绩解码（time / number / multi + 特殊值）
   │
Stage 3  打乱规范化（333mbf 多行还原）
   │
Stage 4  轮次格式归一化（best/average/mean 一致性校验）
   │
Stage 5  特征工程（选手、项目、对抗、时间上下文）
   │
Stage 6  时间分割与索引生成
   │
Stage 7  导出 Parquet + 数据卡校验
```

## 6. 性能策略

| 策略 | 说明 |
| --- | --- |
| Polars 替代 Pandas | 660 万行场景下内存效率提升 3–5 倍 |
| Parquet 列式存储 | 支持列裁剪与谓词下推 |
| 特征缓存 | 高频访问的选手特征持久化 |
| 流式加载器 | 支持大规模训练与内存受限环境 |

## 7. 数据质量检查清单

- [ ] 主键唯一性与外键完整性（persons / competitions / events）
- [ ] 成绩值域合法性（正值范围、特殊值分布）
- [ ] 多盲解码往返一致性（encode(decode(v)) == v）
- [ ] 打乱序列长度与项目匹配率
- [ ] average 重建与官方值一致率 ≥ 阈值
- [ ] 时间戳单调性与时区一致性
- [ ] 分割索引与原始表行数对账

## 8. 后续阅读

- [数据划分策略 →](/zh/data/splits)
- [评估协议与分层 →](/zh/evaluation/protocol)
- [开发计划 · 阶段一任务分解 →](/zh/plan/phase-1)
