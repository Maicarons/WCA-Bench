"""Data layer public API. Must not import tasks/baselines/evaluation."""

from wca_bench.data.decoders import (
    DNF,
    DNS,
    NO_RESULT,
    decode_multi,
    decode_result_value,
    encode_multi,
    format_time_centiseconds,
)
from wca_bench.data.features import build_competition_features, build_result_features
from wca_bench.data.loader import WCABenchData, load_dataset
from wca_bench.data.schema import EVENT_FORMATS, FORMATS, ROUND_TYPES
from wca_bench.data.splits import (
    TIME_SLICES,
    TRAIN_END,
    assign_split,
    freeze_stats,
    time_slice,
)

__all__ = [
    "DNF",
    "DNS",
    "NO_RESULT",
    "EVENT_FORMATS",
    "FORMATS",
    "ROUND_TYPES",
    "TRAIN_END",
    "TIME_SLICES",
    "WCABenchData",
    "assign_split",
    "build_competition_features",
    "build_result_features",
    "decode_multi",
    "decode_result_value",
    "encode_multi",
    "format_time_centiseconds",
    "freeze_stats",
    "load_dataset",
    "time_slice",
]
