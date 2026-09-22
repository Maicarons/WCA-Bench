#!/usr/bin/env python3
"""Static sanity checks for the WCA-Bench LaTeX sources (English and Chinese).

This tool lets anyone verify the paper's internal consistency without a TeX
installation. For each language version it checks that

1. every ``\\input{...}`` target exists on disk;
2. every citation key used in a ``\\cite``-family command is defined in the
   shared ``references.bib`` (unused entries are reported as warnings);
3. ``\\begin{env}`` and ``\\end{env}`` are balanced in every source file.

Both ``main.tex`` (English) and ``zh/main.tex`` (Chinese) are checked when
present, sharing the single ``references.bib`` at the repository paper root.

Exit status is 0 when there are no errors and non-zero otherwise. Warnings do
not fail the run.

Usage:
    python check_bib.py
    python check_bib.py --quiet
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PAPER_DIR = Path(__file__).resolve().parent
BIB_FILE = PAPER_DIR / "references.bib"

# Roots to check: English first, then Chinese if it exists.
ROOTS = [PAPER_DIR / "main.tex"]
_ZH_MAIN = PAPER_DIR / "zh" / "main.tex"
if _ZH_MAIN.exists():
    ROOTS.append(_ZH_MAIN)

INPUT_RE = re.compile(r"\\input\{([^}]+)\}")
CITE_RE = re.compile(r"\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]+)\}")
BIB_KEY_RE = re.compile(r"@\w+\s*\{\s*([^,\s]+)\s*,")


def strip_comments(line: str) -> str:
    """Remove a LaTeX comment, respecting escaped percent signs."""
    out = []
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == "\\" and i + 1 < len(line):
            out.append(line[i : i + 2])
            i += 2
            continue
        if ch == "%":
            break
        out.append(ch)
        i += 1
    return "".join(out)


def collect_sources(root: Path) -> list[Path]:
    """Return root plus every file it \\input-s, recursively."""
    if not root.exists():
        raise FileNotFoundError(f"root file not found: {root}")

    seen: list[Path] = []
    queue = [root]
    while queue:
        path = queue.pop(0)
        if path in seen:
            continue
        seen.append(path)
        if path.suffix != ".tex":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for raw in INPUT_RE.findall(text):
            target = raw.strip()
            if not target.endswith(".tex"):
                target += ".tex"
            candidate = (path.parent / target).resolve()
            if candidate.exists():
                queue.append(candidate)
    return seen


def check_inputs(root: Path) -> list[str]:
    """Verify that every \\input target referenced from root exists."""
    errors: list[str] = []
    text = root.read_text(encoding="utf-8", errors="replace")
    for raw in INPUT_RE.findall(text):
        target = raw.strip()
        if not target.endswith(".tex"):
            target += ".tex"
        candidate = root.parent / target
        if not candidate.exists():
            errors.append(f"\\input target does not exist: {target}")
    return errors


def check_citations(sources: list[Path], defined: set[str]) -> tuple[list[str], list[str], int]:
    """Return (errors, warnings, number_of_unique_citation_keys)."""
    errors: list[str] = []
    warnings: list[str] = []

    used: dict[str, list[str]] = {}
    for path in sources:
        if path.suffix != ".tex":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            line = strip_comments(line)
            for group in CITE_RE.findall(line):
                for key in group.split(","):
                    key = key.strip()
                    if key:
                        used.setdefault(key, []).append(path.name)

    for key, where in sorted(used.items()):
        if key not in defined:
            errors.append(
                f"undefined citation key '{key}' used in {', '.join(sorted(set(where)))}"
            )

    unused = sorted(defined.difference(used))
    for key in unused:
        warnings.append(f"bibliography entry never cited: '{key}'")

    return errors, warnings, len(used)


def check_environments(sources: list[Path]) -> list[str]:
    """Check that \\begin / \\end are balanced within each file."""
    errors: list[str] = []
    for path in sources:
        if path.suffix != ".tex":
            continue
        stack: list[tuple[str, int]] = []
        for lineno, raw in enumerate(
            path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1
        ):
            line = strip_comments(raw)
            for match in re.finditer(r"\\(begin|end)\{([^}]+)\}", line):
                kind, env = match.group(1), match.group(2)
                if kind == "begin":
                    stack.append((env, lineno))
                else:
                    if not stack:
                        errors.append(
                            f"{path.name}:{lineno}: \\end{{{env}}} without matching \\begin"
                        )
                    elif stack[-1][0] != env:
                        open_env, open_line = stack[-1]
                        errors.append(
                            f"{path.name}:{lineno}: \\end{{{env}}} closes "
                            f"\\begin{{{open_env}}} opened at line {open_line}"
                        )
                        stack.pop()
                    else:
                        stack.pop()
        for env, lineno in stack:
            errors.append(f"{path.name}:{lineno}: \\begin{{{env}}} never closed")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quiet", action="store_true", help="only print problems")
    args = parser.parse_args()

    if not BIB_FILE.exists():
        sys.stderr.write(f"ERROR: bibliography file not found: {BIB_FILE}\n")
        return 2

    defined = set(BIB_KEY_RE.findall(BIB_FILE.read_text(encoding="utf-8")))
    if not args.quiet:
        print(f"Bibliography: {BIB_FILE.name} ({len(defined)} entries)")

    all_errors: list[str] = []
    all_warnings: list[str] = []

    for root in ROOTS:
        label = root.relative_to(PAPER_DIR).as_posix()
        try:
            sources = collect_sources(root)
        except FileNotFoundError as exc:
            all_errors.append(str(exc))
            continue

        errors = check_inputs(root)
        c_errors, warnings, n_keys = check_citations(sources, defined)
        errors.extend(c_errors)
        errors.extend(check_environments(sources))

        if not args.quiet:
            print(
                f"[{label}] {len(sources)} source file(s), "
                f"{n_keys} unique citation keys"
            )
        all_errors.extend(f"[{label}] {e}" for e in errors)
        all_warnings.extend(f"[{label}] {w}" for w in warnings)

    for warning in all_warnings:
        print(f"WARNING: {warning}")

    if all_errors:
        for err in all_errors:
            print(f"ERROR: {err}")
        print(f"\nFAILED with {len(all_errors)} error(s).")
        return 1

    if not args.quiet:
        print("OK: inputs, citations and environments are consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
