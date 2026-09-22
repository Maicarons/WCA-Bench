# Contributing to WCA-Bench

Thank you for your interest in WCA-Bench. This project is a **standardized benchmark**, so
contributions must first protect the consistency and reproducibility of the evaluation protocol.

Simplified Chinese version: [`CONTRIBUTING_zh.md`](CONTRIBUTING_zh.md).

## Development environment

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux
pip install -e ".[dev,fast,boost]"
```

Verify your setup:

```bash
pytest
python scripts/generate_synthetic.py
python scripts/build_dataset.py --source synthetic
python scripts/run_all_baselines.py --mode small
```

## Layout and dependency direction

```text
tasks        ──► data
baselines    ──► tasks ──► data
evaluation   ──► tasks + data
leaderboard  ──► evaluation
```

`src/wca_bench/data` must **never** import `tasks`, `baselines`, `evaluation`, or `leaderboard`.
This is enforced by `tests/unit/test_import_policy.py`.

## Commit conventions

- Branches: `<type>/<scope>-<desc>`, e.g. `feat/dnf-xgboost`
- Commits: Conventional Commits, e.g. `feat(dnf): add XGBoost baseline`
- Issues: `<type>: <short description>`, e.g. `bug: multi-blind decoding edge case`

## Pull request requirements

1. Code review: at least one approval.
2. Unit tests pass and core-module coverage does not decrease.
3. Any change to a task definition or the evaluation protocol **must** update `docs/` in the same
   pull request.
4. No future information leakage: every feature function must take an explicit `as_of` argument.
5. New baselines must produce a complete `report/` structure, including `significance`.

## Changing a task definition

| Change type | Handling |
| --- | --- |
| Clarifying (semantics unchanged) | Update directly; patch version |
| Additive (new metric or subset) | Minor version; primary metric unchanged |
| Breaking (inputs or outputs change) | Major version; a separate leaderboard is created |

## Code of conduct

Please read [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

## Data and ethics

- Use only the official public WCA export.
- Do not use the data for gambling, individual discrimination, or similar purposes
  (see [`datacard.md`](datacard.md)).
- Preserve the WCA attribution statement when redistributing processed data.
