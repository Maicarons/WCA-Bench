"""Deep learning baselines package (optional torch).

CPU-first by design: these baselines run on modest sample sizes (2k–80k rows)
with many small per-competition forward passes, i.e. the workload is
**latency-sensitive rather than throughput-sensitive**. On such workloads CPU
typically matches or beats GPU once kernel-launch and transfer overheads are
counted. GPU acceleration only pays off for the full rolling-window protocol
across many seeds with large batches, and can be requested explicitly via
``device="auto"`` / ``WCA_BENCH_DEVICE=cuda``.
"""

from wca_bench.baselines.deep.lstm_result import lstm_result_predict

__all__ = ["lstm_result_predict"]
