"""Domain decoders for WCA result values, multi-blind, scrambles, and averages.

Official multi-blind encoding (WCA Results Export v2):
  old: 1SSAATTTTT
       solved = 99 - SS, attempted = AA, timeInSeconds = TTTTT
  new: 0DDTTTTTMM
       difference = 99 - DD, timeInSeconds = TTTTT, missed = MM
       solved = difference + missed, attempted = solved + missed
  encode: DD = 99 - (solved - missed), TTTTT = seconds, MM = missed
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from wca_bench.data.schema import DNF, DNS, EVENT_FORMATS, FORMATS, NO_RESULT

__all__ = [
    "DNF",
    "DNS",
    "NO_RESULT",
    "MultiBlindResult",
    "AttemptOutcome",
    "decode_multi",
    "encode_multi",
    "decode_result_value",
    "format_time_centiseconds",
    "normalize_multiblind_scramble",
    "compute_best",
    "compute_average",
    "reconstruct_round",
]


@dataclass(frozen=True)
class MultiBlindResult:
    solved: int
    attempted: int
    time_seconds: int
    missed: int
    version: str  # "old" | "new"

    @property
    def difference(self) -> int:
        return self.solved - self.missed


@dataclass(frozen=True)
class AttemptOutcome:
    """Decoded attempt with a canonical continuous score where available."""

    raw: int
    is_dnf: bool
    is_dns: bool
    is_missing: bool
    score: float | None  # lower-is-better continuous value used for ranking
    unit: str  # time_cs | moves | multi_score | none
    multi: MultiBlindResult | None = None


def decode_multi(value: int) -> MultiBlindResult:
    """Decode a multi-blind integer into solved/attempted/time."""
    if value <= 0:
        raise ValueError(f"multi-blind value must be positive, got {value}")
    s = str(int(value)).zfill(10)
    if len(s) != 10:
        raise ValueError(f"multi-blind value out of range: {value}")
    if s[0] == "1":
        # old 1SSAATTTTT
        ss = int(s[1:3])
        aa = int(s[3:5])
        seconds = int(s[5:10])
        solved = 99 - ss
        attempted = aa
        missed = attempted - solved
        if missed < 0:
            raise ValueError(f"invalid old multi-blind encoding: {value}")
        return MultiBlindResult(solved, attempted, seconds, missed, "old")
    if s[0] == "0":
        # new 0DDTTTTTMM
        dd = int(s[1:3])
        seconds = int(s[3:8])
        mm = int(s[8:10])
        difference = 99 - dd
        missed = mm
        solved = difference + missed
        attempted = solved + missed
        return MultiBlindResult(solved, attempted, seconds, missed, "new")
    raise ValueError(f"unknown multi-blind version digit: {s[0]} (value={value})")


def encode_multi(solved: int, attempted: int, time_seconds: int, *, version: str = "new") -> int:
    """Encode multi-blind fields to the WCA integer representation."""
    if attempted > 99:
        raise ValueError("multi-blind supports at most 99 attempted cubes")
    if time_seconds > 99999:
        raise ValueError("multi-blind supports at most 99999 seconds")
    missed = attempted - solved
    if missed < 0:
        raise ValueError("attempted must be >= solved")
    if version == "new":
        # new 0DDTTTTTMM: DD*10^7 + TTTTT*100 + MM
        difference = solved - missed
        if difference < 0:
            raise ValueError(
                "new multi-blind encoding requires solved >= missed "
                f"(non-negative points); got solved={solved}, missed={missed}"
            )
        dd = 99 - difference
        if dd < 0 or dd > 99:
            raise ValueError(f"DD out of range for solved={solved} missed={missed}")
        return dd * 10_000_000 + int(time_seconds) * 100 + missed
    if version == "old":
        # old 1SSAATTTTT = 1*10^9 + SS*10^7 + AA*10^5 + TTTTT
        ss = 99 - solved
        if ss < 0 or ss > 99:
            raise ValueError(f"SS out of range for solved={solved}")
        return 1_000_000_000 + ss * 10_000_000 + attempted * 100_000 + int(time_seconds)
    raise ValueError(f"unknown multi-blind version: {version}")


def format_time_centiseconds(cs: int) -> str:
    """Format centiseconds as m:ss.hh or ss.hh."""
    if cs < 0:
        return "DNF" if cs == DNF else "DNS" if cs == DNS else str(cs)
    total_cs = int(cs)
    hours, rem = divmod(total_cs, 360000)
    minutes, rem = divmod(rem, 6000)
    seconds, centis = divmod(rem, 100)
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}.{centis:02d}"
    if minutes:
        return f"{minutes}:{seconds:02d}.{centis:02d}"
    return f"{seconds}.{centis:02d}"


def _multi_score(multi: MultiBlindResult) -> float:
    """Lower is better: more solved is better, fewer seconds is better."""
    return (100 - multi.solved) * 1_000_000 + multi.time_seconds + multi.missed


def decode_result_value(value: int | float | None, event_id: str) -> AttemptOutcome:
    """Decode one WCA result/attempt value for a given event."""
    if value is None:
        return AttemptOutcome(NO_RESULT, False, False, True, None, "none")
    v = int(value)
    if v == DNF:
        return AttemptOutcome(DNF, True, False, False, float("inf"), "none")
    if v == DNS:
        return AttemptOutcome(DNS, False, True, False, float("inf"), "none")
    if v == NO_RESULT:
        return AttemptOutcome(NO_RESULT, False, False, True, None, "none")

    fmt = EVENT_FORMATS.get(event_id, {}).get("format", "time")
    if fmt == "multi":
        multi = decode_multi(v)
        return AttemptOutcome(v, False, False, False, _multi_score(multi), "multi_score", multi)
    if fmt == "number":
        # fewest moves: raw number of moves; averages stored as 100*avg
        return AttemptOutcome(v, False, False, False, float(v), "moves")
    return AttemptOutcome(v, False, False, False, float(v), "time_cs")


def normalize_multiblind_scramble(scramble: str | None) -> list[str]:
    """Restore 333mbf scrambles from TSV pipe-joined form to a list of scrambles."""
    if not scramble:
        return []
    text = scramble.replace("\r\n", "\n").replace("\r", "\n")
    if "|" in text:
        parts = [p.strip() for p in text.split("|")]
    else:
        parts = [p.strip() for p in text.split("\n")]
    return [p for p in parts if p]


def _valid_scores(attempts: Sequence[AttemptOutcome]) -> list[float]:
    return [a.score for a in attempts if a.score is not None and a.score != float("inf")]


def compute_best(attempts: Sequence[AttemptOutcome], event_id: str) -> int:
    """Compute WCA best single value from decoded attempts."""
    usable = [a for a in attempts if not a.is_missing and not a.is_dns]
    if not usable:
        return NO_RESULT
    valid = [a for a in usable if not a.is_dnf]
    if not valid:
        # all DNF among usable attempts → best is DNF
        return DNF
    fmt = EVENT_FORMATS.get(event_id, {}).get("format", "time")
    if fmt == "multi":
        # smaller encoded value is better by design
        return min(a.raw for a in valid)
    if fmt == "number":
        return int(min(a.score for a in valid if a.score is not None))
    return int(min(a.score for a in valid if a.score is not None))


def compute_average(
    attempts: Sequence[AttemptOutcome], format_id: str, event_id: str
) -> int:
    """Compute WCA average / mean according to format rules.

    Returns 0 when the format has no average (best-of-N).
    """
    meta = FORMATS.get(format_id)
    if meta is None:
        return NO_RESULT
    if not meta.get("average"):
        return NO_RESULT

    n = int(meta["attempts"])
    seq = list(attempts)[:n]
    if len(seq) < n:
        seq = seq + [AttemptOutcome(0, False, False, True, None, "none")] * (n - len(seq))

    fmt = EVENT_FORMATS.get(event_id, {}).get("format", "time")

    if meta["short"] == "mo3":
        if any(a.is_dnf or a.is_dns or a.is_missing for a in seq):
            return DNF
        if fmt == "multi":
            # mean of 3 multi-blind is not used historically; keep defensive path
            scores = [float(a.score or 0.0) for a in seq]
            return int(sum(scores) / len(scores)) if scores else DNF
        if fmt == "number":
            # FMC averages stored as 100 * mean
            vals = [float(a.score or 0.0) for a in seq]
            return int(round(sum(vals) / len(vals) * 100))
        vals = [float(a.score or 0.0) for a in seq]
        return int(round(sum(vals) / len(vals)))

    # average of 5
    if fmt == "multi":
        valid = [a for a in seq if not a.is_dnf and not a.is_dns and not a.is_missing]
        if len(valid) < 3:
            return DNF
        # reconstruct properly using DNFs (a single DNF occupies the worst slot)
        dnf_count = sum(1 for a in seq if a.is_dnf or a.is_dns or a.is_missing)
        if dnf_count >= 2:
            return DNF
        ordered = sorted(
            seq,
            key=lambda a: (
                float("inf") if (a.is_dnf or a.is_dns or a.is_missing) else (a.score or 0)
            ),
        )
        middle = ordered[1:4]
        if any(a.is_dnf or a.is_dns or a.is_missing for a in middle):
            return DNF
        # average of middle 3 multi scores is not a WCA stored form; use best middle raw
        # Keep a deterministic surrogate: mean of middle scores mapped back via best match
        mean_score = sum(a.score or 0 for a in middle) / 3.0
        # choose the middle attempt closest to mean_score
        nearest = min(middle, key=lambda a: abs((a.score or 0) - mean_score))
        return int(nearest.raw)

    dnf_count = sum(1 for a in seq if a.is_dnf or a.is_dns or a.is_missing)
    if dnf_count >= 2:
        return DNF
    if fmt == "number":
        nums = []
        for a in seq:
            if a.is_dnf or a.is_dns or a.is_missing:
                continue
            nums.append(float(a.score or 0.0))
        if len(nums) < 3:
            return DNF
        # include DNF as +inf for drop logic then drop best and worst
        nums_expanded = list(nums) + [float("inf")] * dnf_count
        nums_expanded = (
            nums_expanded[:5]
            if len(nums_expanded) >= 5
            else nums_expanded + [float("inf")] * (5 - len(nums_expanded))
        )
        nums_expanded = sorted(nums_expanded)[:5]
        center = nums_expanded[1:4]
        if any(x == float("inf") for x in center):
            return DNF
        return int(round(sum(center) / 3.0 * 100))

    expanded: list[float] = []
    for a in seq:
        if a.is_dnf or a.is_dns or a.is_missing:
            expanded.append(float("inf"))
        else:
            expanded.append(float(a.score or 0.0))
    expanded = sorted(expanded)[:5]
    while len(expanded) < 5:
        expanded.append(float("inf"))
    center = expanded[1:4]
    if any(x == float("inf") for x in center):
        return DNF
    return int(round(sum(center) / 3.0))


def reconstruct_round(
    attempt_values: Iterable[int | float | None],
    format_id: str,
    event_id: str,
) -> tuple[int, int]:
    """Rebuild (best, average) from attempt values."""
    decoded = [decode_result_value(v, event_id) for v in attempt_values]
    best = compute_best(decoded, event_id)
    average = compute_average(decoded, format_id, event_id)
    return best, average
