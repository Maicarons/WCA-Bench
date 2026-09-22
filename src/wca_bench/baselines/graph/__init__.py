"""Graph baselines package (optional torch).

CPU-first by design: the person-competition heterogeneous graph covers only a
few thousand nodes per evaluation round and is scored with small batches, so the
workload is **latency-sensitive rather than throughput-sensitive**. GPU kernels
add launch/transfer overhead that usually outweighs the benefit at this scale;
GPU is only worthwhile for the full rolling-window protocol across many seeds
with large batches, and can be requested via ``device="auto"`` /
``WCA_BENCH_DEVICE=cuda``.
"""

from wca_bench.baselines.graph.gnn_placement import gnn_placement_predict

__all__ = ["gnn_placement_predict"]
