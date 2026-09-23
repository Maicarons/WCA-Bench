"""Task suite public API."""

from wca_bench.tasks.base import Baseline, BaseTask, Report, Task
from wca_bench.tasks.dnf.task import DNFTask
from wca_bench.tasks.limit.task import HumanLimitTask
from wca_bench.tasks.placement.task import PlacementTask
from wca_bench.tasks.result_prediction.task import ResultPredictionTask
from wca_bench.tasks.transfer.task import SkillTransferTask

TASK_REGISTRY: dict[str, type[BaseTask]] = {
    "result_prediction": ResultPredictionTask,
    "placement": PlacementTask,
    "dnf": DNFTask,
    "limit": HumanLimitTask,
    "transfer": SkillTransferTask,
}

__all__ = [
    "Task",
    "Baseline",
    "Report",
    "ResultPredictionTask",
    "PlacementTask",
    "DNFTask",
    "HumanLimitTask",
    "SkillTransferTask",
    "TASK_REGISTRY",
]
