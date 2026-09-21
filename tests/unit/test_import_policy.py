"""Import dependency direction policy tests."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "src" / "wca_bench"

FORBIDDEN = {
    "data": {"tasks", "baselines", "evaluation", "leaderboard"},
}


def _imports_in(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                mods.add(a.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                mods.add(node.module)
    return mods


def test_data_does_not_import_upper_layers():
    data_dir = SRC / "data"
    offenders = []
    for py in data_dir.rglob("*.py"):
        mods = _imports_in(py)
        for m in mods:
            top = m.split(".")[0]
            if top == "wca_bench":
                parts = m.split(".")
                if len(parts) > 1 and parts[1] in FORBIDDEN["data"]:
                    offenders.append((py.name, m))
            elif top in FORBIDDEN["data"]:
                offenders.append((py.name, m))
    assert not offenders, f"data layer imports forbidden modules: {offenders}"
