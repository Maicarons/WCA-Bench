# Data Sources and Table Schemas

## 1. Data Sources

WCA-Bench uses the **official public WCA database export**, which includes the following core tables:

| Table | Scale (approx.) | Description |
| --- | --- | --- |
| `persons` | 289k rows | Competitor information: WCA ID, name, nationality, gender |
| `competitions` | 17.7k rows | Competition metadata: date, city, coordinates |
| `results` | 6.6M rows | Result records per person, event, and round, including best and average fields |
| `result_attempts` | — | Individual attempt values for each round |
| `scrambles` | 3.1M rows | Scramble sequences for each round and group |
| `events` | — | The 17 active events and retired events |
| `formats` / `round_types` | — | Scoring formats (ao5, mo3, etc.) and round types (final, semifinal, etc.) |
| `countries` / `continents` | — | Country and continent information |
| `championships` | — | Championship affiliation, including `eligible_country_iso2s_for_championship` |

::: info Version differences in result_attempts
In the v2.0.2 export, `result_attempts` has **dropped** the `id`, `created_at`, and `updated_at` fields to reduce file size. The preprocessing pipeline must not depend on those fields.
:::

## 2. Data Scale

As of 2026, the WCA database contains:

- More than **282,000** competitors
- **16,600+** competitions

The Developer export additionally contains **round configuration, schedule, and venue** information, making it possible to obtain per-round time limits, cutoff times, advancement conditions, and other competition configuration fields.

## 3. Core Table Relationships

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
- `results` links format and round semantics through `(competition_id, event_id, round_type_id, format_id)`

## 4. Key Field Semantics

### 4.1 The results Table

| Field | Semantics | Notes |
| --- | --- | --- |
| `best` | Best result of the round | The encoding depends on `format_id`, see below |
| `average` | Average result of the round | Only present for ao5 / mo3 and similar formats |
| `format_id` | Scoring format | Determines how the value is decoded |
| `round_type_id` | Round type | Final / semifinal / first round, etc. |
| `pos` | Placement | Can serve as the supervision signal for Task 2 |
| `regional_*` / `continental_*` | Regional record flags | Optional features |

### 4.2 Special Value Encoding

| Value | Meaning |
| --- | --- |
| `-1` | DNF (Did Not Finish) |
| `-2` | DNS (Did Not Start) |
| `0` | No result (no record produced in that round) |

### 4.3 The formats Table

| format | Meaning of the value | Example |
| --- | --- | --- |
| `time` | Hundredths of a second | `8653` = 1 minute 26.53 seconds |
| `number` | Raw number (fewest moves only) | `28` = 28 moves |
| `multi` | Multi-blind encoding | `1SSAATTTTT` (old) / `0DDTTTTTMM` (new) |

## 5. Multi-Blind Encoding Format

Results in the multi-blind event (`333mbf`) use a composite encoding:

```text
Old format: 1 S S A A T T T T T
New format: 0 D D T T T T T M M
```

Where:

- The first digit identifies the version (`1` = old, `0` = new)
- `SS` / `DD` = difference encoding (the relationship between the number of attempts and the number of solved cubes)
- `TTTTT` = total time (seconds)
- `MM` = number of unsolved cubes

The decoding logic is described in [Preprocessing Pipeline · Result Value Decoding](/data/pipeline#_1-result-value-decoding).

## 6. Terms of Use and Ethics

- Data copyright belongs to the **World Cube Association** and follows the acceptable use terms for its public data
- For aggregate and statistical purposes only; scenarios such as gambling prediction and individual discrimination are prohibited
- See [Project Scope · Forbidden Use Cases](/guide/scope#_4-forbidden-use-cases)

## 7. Further Reading

- [Preprocessing Pipeline →](/data/pipeline)
- [Data Splitting Strategy →](/data/splits)
