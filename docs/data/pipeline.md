# Preprocessing Pipeline

Preprocessing WCA-Bench data requires handling four classes of domain-specific problems: result value decoding, scramble sequence handling, round format normalization, and temporal leakage protection.

## 1. Result Value Decoding

The meaning of a positive value **depends on the event's format field**:

| format | Meaning of the value | Example |
| --- | --- | --- |
| `time` | Hundredths of a second | `8653` → 1 minute 26.53 seconds |
| `number` | Raw number (fewest moves only) | `28` → 28 moves |
| `multi` | Multi-blind encoding | Must be decoded as `1SSAATTTTT` / `0DDTTTTTMM` |

Special values:

| Value | Meaning | Handling |
| --- | --- | --- |
| `-1` | DNF | Marked as a failure; contributes to DNF-rate statistics but not to averages |
| `-2` | DNS | Marked as not started; usually excluded from training |
| `0` | No result | Treated as missing |

### 1.1 Multi-Blind Decoding Implementation Notes

```python
def decode_multi(value: int) -> tuple[int, int, int]:
    """Decode a multi-blind encoding into (solved, attempted, seconds)."""
    s = str(value).zfill(10)
    if s[0] == "1":                     # old format 1SSAATTTTT
        dd = 99 - int(s[1:3])
        mm = int(s[3:5])
        solved = dd + mm
        attempted = solved + mm
        seconds = int(s[5:10])
    else:                               # new format 0DDTTTTTMM
        dd = int(s[1:3])
        seconds = int(s[3:8])
        mm = int(s[8:10])
        solved = 99 - dd - mm
        attempted = solved + mm
    return solved, attempted, seconds
```

## 2. Scramble Sequence Handling

Scrambles for the `333mbf` event consist of **multiple newline-separated 3x3 scrambles**. In the TSV version, newlines are replaced by the `|` character.

Preprocessing steps:

1. Split on `|`
2. Restore the multi-line scramble sequence
3. Normalize whitespace and escaping
4. Validate that the scramble length matches the event

## 3. Round Format Normalization

Different round formats compute results differently:

| Format | Computation |
| --- | --- |
| best of 3 | Take the best of 3 attempts |
| average of 5 | Discard the best and worst attempts, then take the arithmetic mean of the remaining 3 |
| mean of 3 | Arithmetic mean of 3 attempts |

::: warning Impact of the trimming mechanism
In ao5, **the impact of a single DNF on the final result is amplified** (a DNF usually occupies the "worst" slot and is discarded, but two DNFs make the whole round a DNF). Models need to model this rule effect explicitly rather than simply averaging the attempt values.
:::

The pipeline must:

1. Reconstruct the attempt sequence of each round from `result_attempts`
2. Compute the standardized `average` according to `format_id`
3. Cross-check it against the official `results.average` (and log a warning on mismatch)

## 4. Temporal Leakage Protection

The evaluation protocol must ensure that benchmark computation **uses only information available at the decision time**:

```text
For result prediction at competition t:
    Allowed: all data with competition_date < date(t)
    Forbidden: competition t and any data after it
    Frozen: benchmark statistics such as competitor historical means and world records
```

Implementation conventions:

- All feature function signatures are required to accept an `as_of` timestamp
- Feature caches are bucketed by `as_of` to avoid reuse across time
- An assertion utility `assert_no_leakage(features, target_date)` is provided for testing

## 5. Pipeline Stages

```text
Stage 0  Raw file validation (existence, headers, encoding)
   │
Stage 1  Full-table loading (Polars scan_tsv)
   │
Stage 2  Result decoding (time / number / multi + special values)
   │
Stage 3  Scramble normalization (restore multi-line 333mbf)
   │
Stage 4  Round format normalization (best/average/mean consistency checks)
   │
Stage 5  Feature engineering (competitor, event, head-to-head, temporal context)
   │
Stage 6  Temporal splitting and index generation
   │
Stage 7  Export Parquet + data card validation
```

## 6. Performance Strategy

| Strategy | Description |
| --- | --- |
| Polars instead of Pandas | 3–5× better memory efficiency at 6.6M rows |
| Parquet columnar storage | Supports column pruning and predicate pushdown |
| Feature cache | Persists frequently accessed competitor features |
| Streaming loader | Supports large-scale training and memory-constrained environments |

## 7. Data Quality Checklist

- [ ] Primary key uniqueness and foreign key integrity (persons / competitions / events)
- [ ] Valid result value ranges (range of positive values, distribution of special values)
- [ ] Multi-blind decoding round-trip consistency (encode(decode(v)) == v)
- [ ] Match rate between scramble sequence length and event
- [ ] Consistency rate between reconstructed average and the official value ≥ threshold
- [ ] Timestamp monotonicity and time zone consistency
- [ ] Reconciliation between split indices and raw table row counts

## 8. Further Reading

- [Data Splitting Strategy →](/data/splits)
- [Evaluation Protocol and Stratification →](/evaluation/protocol)
- [Development Plan · Phase 1 Task Breakdown →](/plan/phase-1)
