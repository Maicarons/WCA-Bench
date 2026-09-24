"""Synthetic WCA-like dataset generator for CI, demos, and offline development.

Produces tables aligned with WCA Results Export v2 schema, covering 2003–2026
so temporal splits (train/val/test) are exercisable end-to-end.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from wca_bench.data.decoders import encode_multi
from wca_bench.data.schema import DNF, EVENT_FORMATS, FORMATS
from wca_bench.utils.io import save_table


@dataclass
class SyntheticConfig:
    n_persons: int = 400
    n_competitions: int = 80
    seed: int = 42
    events: tuple[str, ...] = (
        "333",
        "222",
        "444",
        "555",
        "333oh",
        "333fm",
        "pyram",
        "skewb",
        "minx",
        "clock",
        "sq1",
        "333bf",
        "444bf",
        "555bf",
        "333mbf",
        "777",
        "666",
    )
    countries: tuple[tuple[str, str, str], ...] = (
        ("CN", "China", "AS"),
        ("US", "United States", "NA"),
        ("JP", "Japan", "AS"),
        ("DE", "Germany", "EU"),
        ("FR", "France", "EU"),
        ("BR", "Brazil", "SA"),
        ("AU", "Australia", "OC"),
        ("ZA", "South Africa", "AF"),
        ("GB", "United Kingdom", "EU"),
        ("KR", "Korea", "AS"),
    )


# Typical elite single times in centiseconds (approx)
EVENT_BASE = {
    "333": 500,
    "222": 180,
    "444": 2200,
    "555": 4500,
    "666": 9000,
    "777": 14000,
    "333oh": 900,
    "333fm": 25,  # moves
    "333ft": 2500,
    "minx": 3500,
    "pyram": 250,
    "clock": 400,
    "skewb": 280,
    "sq1": 700,
    "333bf": 2000,
    "444bf": 9000,
    "555bf": 18000,
    "333mbf": 0,  # special
}

EVENT_DNF_BASE = {
    "333": 0.02,
    "222": 0.015,
    "444": 0.03,
    "555": 0.035,
    "666": 0.04,
    "777": 0.045,
    "333oh": 0.03,
    "333fm": 0.06,
    "minx": 0.03,
    "pyram": 0.02,
    "clock": 0.03,
    "skewb": 0.02,
    "sq1": 0.04,
    "333bf": 0.25,
    "444bf": 0.40,
    "555bf": 0.45,
    "333mbf": 0.15,
}


def _random_dates(rng: np.random.Generator, n: int, start: date, end: date) -> list[date]:
    span = (end - start).days
    offsets = rng.integers(0, max(span, 1), size=n)
    return [start + timedelta(days=int(o)) for o in offsets]


def generate_synthetic_dataset(
    out_dir: str | Path,
    config: SyntheticConfig | None = None,
    *,
    small: bool = False,
) -> dict[str, Path]:
    """Write synthetic WCA-like TSV/CSV tables under out_dir."""
    cfg = config or SyntheticConfig()
    if small:
        cfg = SyntheticConfig(
            n_persons=80,
            n_competitions=24,
            seed=cfg.seed,
            events=("333", "222", "444", "333oh", "333fm", "pyram", "333bf", "333mbf"),
        )
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(cfg.seed)

    continents = pd.DataFrame(
        [
            {"id": "AF", "name": "Africa"},
            {"id": "AS", "name": "Asia"},
            {"id": "EU", "name": "Europe"},
            {"id": "NA", "name": "North America"},
            {"id": "OC", "name": "Oceania"},
            {"id": "SA", "name": "South America"},
        ]
    )
    countries = pd.DataFrame(
        [
            {"id": iso, "name": name, "continent_id": cont, "iso2": iso}
            for iso, name, cont in cfg.countries
        ]
    )
    events = pd.DataFrame(
        [
            {
                "id": eid,
                "name": EVENT_FORMATS[eid]["name"],
                "format": EVENT_FORMATS[eid]["format"],
                "rank": i + 1,
            }
            for i, eid in enumerate(cfg.events)
            if eid in EVENT_FORMATS
        ]
    )
    formats = pd.DataFrame(
        [
            {
                "id": fid,
                "name": meta["name"],
                "short_name": meta["short"],
                "expected_solve_count": meta["attempts"],
                "sort_by": "average" if meta["average"] else "best",
            }
            for fid, meta in FORMATS.items()
        ]
    )
    round_types = pd.DataFrame(
        [
            {"id": "1", "name": "First Round", "rank": 1},
            {"id": "2", "name": "Second Round", "rank": 2},
            {"id": "f", "name": "Final", "rank": 3},
        ]
    )

    persons_rows = []
    skill: dict[str, dict[str, float]] = {}
    dnf_bias: dict[str, float] = {}
    for i in range(cfg.n_persons):
        wca_id = f"20{i // 20 + 8:02d}{i % 20 + 1:02d}{i % 97 + 1:02d}"
        # ensure unique-ish
        wca_id = f"20{8 + (i % 15):02d}{(i % 28) + 1:02d}{(i * 7) % 97 + 1:02d}"
        country = cfg.countries[int(rng.integers(0, len(cfg.countries)))]
        birth_year = int(rng.integers(1975, 2012))
        gender = rng.choice(["m", "f", "o"], p=[0.75, 0.22, 0.03])
        persons_rows.append(
            {
                "wca_id": wca_id,
                "sub_id": 1,
                "name": f"Competitor {i:04d}",
                "country_id": country[0],
                "continent_id": country[2],
                "gender": gender,
                "birth_year": birth_year,
                "birth_month": int(rng.integers(1, 13)),
            }
        )
        # latent skill: lower multiplier = faster
        base = float(rng.lognormal(mean=0.0, sigma=0.55))
        skill[wca_id] = {}
        dnf_bias[wca_id] = float(rng.uniform(0.4, 2.0))
        for eid in cfg.events:
            # later first-seen events get worse skill if entered
            skill[wca_id][eid] = base * float(rng.lognormal(mean=0.15, sigma=0.25))

    persons = pd.DataFrame(persons_rows)

    comps_rows = []
    start = date(2004, 1, 1)
    end = date(2026, 8, 31)
    # ensure coverage across split windows
    forced = [
        date(2010, 5, 1),
        date(2015, 6, 15),
        date(2018, 9, 1),
        date(2021, 3, 20),
        date(2023, 4, 10),
        date(2024, 8, 5),
        date(2025, 2, 15),
        date(2025, 9, 12),
        date(2026, 3, 8),
    ]
    dates = forced + _random_dates(rng, max(cfg.n_competitions - len(forced), 0), start, end)
    dates = dates[: cfg.n_competitions]
    for i, d in enumerate(dates):
        country = cfg.countries[int(rng.integers(0, len(cfg.countries)))]
        comps_rows.append(
            {
                "id": f"Comp{i:04d}2026",
                "name": f"Synthetic Open {i:03d}",
                "city_name": f"City{i}",
                "country_id": country[0],
                "start_date": d.isoformat(),
                "end_date": (d + timedelta(days=1)).isoformat(),
                "latitude_microdegrees": int(rng.integers(-50_000_000, 50_000_000)),
                "longitude_microdegrees": int(rng.integers(-150_000_000, 150_000_000)),
            }
        )
    competitions = pd.DataFrame(comps_rows)

    results_rows = []
    attempt_rows = []
    scramble_rows = []
    result_id = 1
    scramble_id = 1
    person_ids = persons["wca_id"].tolist()

    for comp in comps_rows:
        comp_date = date.fromisoformat(str(comp["start_date"]))
        n_entered = int(rng.integers(8, min(cfg.n_persons, 40) + 1))
        entrants = rng.choice(person_ids, size=n_entered, replace=False)
        n_events = int(rng.integers(2, min(len(cfg.events), 7) + 1))
        comp_events = list(rng.choice(cfg.events, size=n_events, replace=False))

        for eid_raw in comp_events:
            eid = str(eid_raw)
            fmt_choice = rng.choice(["1", "3", "a", "m"], p=[0.1, 0.25, 0.55, 0.10])
            # multi-blind / fmc tend to use mo3/best-of
            if eid == "333fm":
                fmt_choice = rng.choice(["1", "m", "3"], p=[0.3, 0.4, 0.3])
            if eid in {"333mbf", "444bf", "555bf"}:
                fmt_choice = rng.choice(["1", "3", "a"], p=[0.35, 0.45, 0.2])
            if eid in {"666", "777"}:
                fmt_choice = rng.choice(["1", "m", "a"], p=[0.3, 0.4, 0.3])
            n_attempts = FORMATS[fmt_choice]["attempts"]
            round_type = rng.choice(["1", "2", "f"], p=[0.55, 0.25, 0.20])

            performances = []
            for pid in entrants:
                mult = skill[pid][eid]
                # mild improvement over calendar time
                years = (comp_date.year - 2004) / 22.0
                trend = 1.0 - 0.25 * years
                dnf_p = min(0.85, EVENT_DNF_BASE.get(eid, 0.03) * dnf_bias[pid])
                attempts = []
                for _ in range(n_attempts):
                    if rng.random() < dnf_p:
                        attempts.append(DNF)
                        continue
                    if eid == "333mbf":
                        # multi-blind synthetic encoding (new format needs solved >= missed)
                        solved = int(np.clip(rng.poisson(lam=max(2, 3 * mult)) + 2, 2, 30))
                        missed = int(rng.poisson(lam=max(0.2, 0.5 * mult)))
                        missed = min(missed, max(solved - 1, 0))
                        attempted = int(solved + missed)
                        seconds = int(np.clip(rng.normal(2400, 600), 600, 6000))
                        attempts.append(encode_multi(solved, attempted, seconds, version="new"))
                    elif EVENT_FORMATS[eid]["format"] == "number":
                        mu = EVENT_BASE[eid] * mult * trend
                        attempts.append(int(np.clip(rng.normal(mu, 1.2), 18, 40)))
                    else:
                        mu = EVENT_BASE[eid] * mult * trend
                        sigma = mu * 0.08
                        attempts.append(int(np.clip(rng.normal(mu, sigma), max(1, mu * 0.4), mu * 4)))
                performances.append((pid, attempts))

            # compute best/average
            from wca_bench.data.decoders import reconstruct_round

            # rank by average if format has average else best
            scored = []
            for pid, attempts in performances:
                best, avg = reconstruct_round(attempts, fmt_choice, eid)
                scored.append((pid, attempts, best, avg))
            if FORMATS[fmt_choice]["average"]:
                scored.sort(key=lambda x: (x[3] == 0 or x[3] == DNF, x[3] if x[3] > 0 else 10**12))
            else:
                scored.sort(key=lambda x: (x[2] == DNF or x[2] == 0, x[2] if x[2] > 0 else 10**12))

            # scramble rows (one group)
            if eid == "333mbf":
                scramble = "R U R' U' | F2 D L2 | B2 U2 F' "
            elif EVENT_FORMATS[eid]["format"] == "number":
                scramble = "R U R' U"
            else:
                scramble = "R U R' U' F2 D L2 B2 U2 F' L D2 R' U B' D' F R2 L U' D B F' R U2"
            scramble_rows.append(
                {
                    "id": scramble_id,
                    "competition_id": comp["id"],
                    "event_id": eid,
                    "round_type_id": round_type,
                    "group_id": "A",
                    "scramble": scramble,
                }
            )
            scramble_id += 1

            for pos, (pid, attempts, best, avg) in enumerate(scored, start=1):
                results_rows.append(
                    {
                        "id": result_id,
                        "pos": pos,
                        "person_id": pid,
                        "person_name": persons.loc[persons["wca_id"] == pid, "name"].iloc[0],
                        "country_id": persons.loc[persons["wca_id"] == pid, "country_id"].iloc[0],
                        "competition_id": comp["id"],
                        "event_id": eid,
                        "round_type_id": round_type,
                        "format_id": fmt_choice,
                        "best": best,
                        "average": avg,
                        "regional_single_record": "",
                        "regional_average_record": "",
                        "start_date": comp["start_date"],
                    }
                )
                for aidx, aval in enumerate(attempts, start=1):
                    attempt_rows.append(
                        {
                            "result_id": result_id,
                            "attempt_number": aidx,
                            "value": aval,
                        }
                    )
                result_id += 1

    results = pd.DataFrame(results_rows)
    result_attempts = pd.DataFrame(attempt_rows)
    scrambles = pd.DataFrame(scramble_rows)
    championships = pd.DataFrame(
        columns=["id", "competition_id", "championship_type"]
    )

    paths = {
        "persons": save_table(persons, out_dir / "WCA_export_Persons.tsv"),
        "competitions": save_table(competitions, out_dir / "WCA_export_Competitions.tsv"),
        "results": save_table(results, out_dir / "WCA_export_Results.tsv"),
        "result_attempts": save_table(result_attempts, out_dir / "WCA_export_ResultAttempts.tsv"),
        "scrambles": save_table(scrambles, out_dir / "WCA_export_Scrambles.tsv"),
        "events": save_table(events, out_dir / "WCA_export_Events.tsv"),
        "formats": save_table(formats, out_dir / "WCA_export_Formats.tsv"),
        "round_types": save_table(round_types, out_dir / "WCA_export_RoundTypes.tsv"),
        "countries": save_table(countries, out_dir / "WCA_export_Countries.tsv"),
        "continents": save_table(continents, out_dir / "WCA_export_Continents.tsv"),
        "championships": save_table(championships, out_dir / "WCA_export_Championships.tsv"),
    }
    meta = {
        "export_date": pd.Timestamp.now("UTC").isoformat(),
        "export_format_version": "synthetic-2.0.2-compatible",
        "n_persons": int(len(persons)),
        "n_competitions": int(len(competitions)),
        "n_results": int(len(results)),
        "n_attempts": int(len(result_attempts)),
        "seed": cfg.seed,
    }
    meta_path = out_dir / "metadata.json"
    pd.Series(meta).to_json(meta_path)
    paths["metadata"] = meta_path
    return paths
