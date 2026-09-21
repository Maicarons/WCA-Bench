# 数据来源与表结构

## 1. 数据来源

WCA-Bench 使用 **WCA 官方公开数据库导出**，包含以下核心表：

| 表 | 规模（约） | 说明 |
| --- | --- | --- |
| `persons` | 289k 行 | 选手信息：WCA ID、姓名、国籍、性别 |
| `competitions` | 17.7k 行 | 比赛元数据：日期、城市、坐标 |
| `results` | 660 万行 | 每人每项每轮的成绩记录，含 best、average 字段 |
| `result_attempts` | — | 每轮的单次尝试值 |
| `scrambles` | 310 万行 | 每轮每组的打乱序列 |
| `events` | — | 17 个现役项目和已废止项目 |
| `formats` / `round_types` | — | 计分格式（ao5、mo3 等）与轮次类型（决赛、半决赛等） |
| `countries` / `continents` | — | 国家和地区信息 |
| `championships` | — | 锦标赛归属，含 `eligible_country_iso2s_for_championship` |

::: info 关于 result_attempts 的版本差异
在 v2.0.2 导出中，`result_attempts` 已**移除** `id`、`created_at`、`updated_at` 字段以减小文件体积。预处理管线不应依赖这些字段。
:::

## 2. 数据规模

截至 2026 年，WCA 数据库包含：

- 超过 **282,000** 名选手
- **16,600+** 场比赛

Developer 导出额外包含**轮次配置、赛程、场馆**等信息，支持获取每轮的限时、及格线、晋级条件等比赛配置字段。

## 3. 核心表关系

```text
persons ──┐
          ├──► results ──► result_attempts
competitions ─┘   │
                  ├──► scrambles
events ───────────┘
formats ──────────┘
round_types ──────┘
countries ─► continents
championships ──► competitions
```

- `persons.WCA ID` ↔ `results.person_id`
- `competitions.id` ↔ `results.competition_id`
- `events.id` ↔ `results.event_id`
- `results` 通过 `(competition_id, event_id, round_type_id, format_id)` 关联格式与轮次语义

## 4. 关键字段语义

### 4.1 results 表

| 字段 | 语义 | 注意事项 |
| --- | --- | --- |
| `best` | 该轮最优成绩 | 编码取决于 `format_id`，见下 |
| `average` | 该轮平均成绩 | 仅 ao5 / mo3 等格式存在 |
| `format_id` | 计分格式 | 决定数值解码方式 |
| `round_type_id` | 轮次类型 | 决赛 / 半决赛 / 第一轮等 |
| `pos` | 名次 | 可用于任务二监督信号 |
| `regional_*` / ` continental_*` | 地区记录标记 | 可选特征 |

### 4.2 特殊值编码

| 值 | 含义 |
| --- | --- |
| `-1` | DNF（Did Not Finish，未完成） |
| `-2` | DNS（Did Not Start，未开始） |
| `0` | 无成绩（该轮未产生记录） |

### 4.3 formats 表

| format | 数值含义 | 示例 |
| --- | --- | --- |
| `time` | 百分之一秒 | `8653` = 1 分 26.53 秒 |
| `number` | 原始数字（仅最少步数） | `28` = 28 步 |
| `multi` | 多盲编码 | `1SSAATTTTT`（旧）/ `0DDTTTTTMM`（新） |

## 5. 多盲编码格式

多盲项目（`333mbf`）的成绩使用复合编码：

```text
旧版格式：1 S S A A T T T T T
新版格式：0 D D T T T T T M M
```

其中：

- 首位标识版本（`1` = 旧，`0` = 新）
- `SS` / `DD` = 差值编码（尝试数与完成数的关系）
- `TTTTT` = 总用时（秒）
- `MM` = 未完成数

具体解码逻辑见[预处理管线 · 成绩值解码](/data/pipeline#_1-成绩值解码)。

## 6. 使用条款与伦理

- 数据版权归 **World Cube Association** 所有，遵循其公开数据的允许使用条款
- 仅用于聚合与统计用途，禁止用于赌博预测、个体歧视等场景
- 详见[项目范围 · 明确禁止的使用场景](/guide/scope#_4-明确禁止的使用场景)

## 7. 后续阅读

- [预处理管线 →](/data/pipeline)
- [数据划分策略 →](/data/splits)
