"""Unit tests for multi-blind / result value decoders."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import pytest

from wca_bench.data.decoders import (
    DNF,
    decode_multi,
    decode_result_value,
    encode_multi,
    format_time_centiseconds,
    reconstruct_round,
)


def test_multi_roundtrip_new():
    for solved, attempted, seconds in [
        (10, 10, 3600),
        (5, 7, 1234),
        (1, 1, 60),
        (20, 22, 4000),
    ]:
        enc = encode_multi(solved, attempted, seconds, version="new")
        dec = decode_multi(enc)
        assert dec.solved == solved
        assert dec.attempted == attempted
        assert dec.time_seconds == seconds
        assert dec.missed == attempted - solved
        assert enc == encode_multi(dec.solved, dec.attempted, dec.time_seconds, version="new")


def test_multi_roundtrip_old():
    for solved, attempted, seconds in [(9, 9, 3000), (3, 5, 999)]:
        enc = encode_multi(solved, attempted, seconds, version="old")
        dec = decode_multi(enc)
        assert dec.solved == solved
        assert dec.attempted == attempted
        assert dec.time_seconds == seconds


def test_multi_official_new_formula():
    # difference = 99 - DD; solved = difference + missed
    # e.g. solved=12, missed=2 => attempted=14, difference=10, DD=89
    enc = encode_multi(12, 14, 2500, version="new")
    assert str(enc).zfill(10) == "0890250002"
    dec = decode_multi(enc)
    assert dec.solved == 12
    assert dec.missed == 2
    assert dec.difference == 10


def test_special_values():
    o = decode_result_value(-1, "333")
    assert o.is_dnf
    o = decode_result_value(-2, "333")
    assert o.is_dns
    o = decode_result_value(0, "333")
    assert o.is_missing


def test_time_decode():
    o = decode_result_value(8653, "333")
    assert o.score == 8653
    assert format_time_centiseconds(8653) == "1:26.53"


def test_best_and_average_ao5():
    # attempts: 1000, 1010, 1020, 1030, 2000 -> best=1000, avg=1020
    best, avg = reconstruct_round([1000, 1010, 1020, 1030, 2000], "a", "333")
    assert best == 1000
    assert avg == 1020
    # one DNF is dropped as worst
    best, avg = reconstruct_round([1000, 1010, 1020, 1030, DNF], "a", "333")
    assert best == 1000
    assert avg == 1020
    # two DNFs => average DNF
    best, avg = reconstruct_round([1000, DNF, 1020, 1030, DNF], "a", "333")
    assert best == 1000
    assert avg == DNF


def test_mean_of_three():
    best, avg = reconstruct_round([1000, 1100, 1200], "m", "333")
    assert best == 1000
    assert avg == 1100
    best, avg = reconstruct_round([1000, DNF, 1200], "m", "333")
    assert avg == DNF


def test_fmc_average_scaled():
    best, avg = reconstruct_round([25, 28, 30], "m", "333fm")
    assert best == 25
    assert avg == int(round((25 + 28 + 30) / 3 * 100))


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
