"""Evaluation framework: metrics, protocol, stratification, significance."""

from wca_bench.evaluation.metrics import (
    auc_pr,
    auc_roc,
    brier_score,
    calibration_error,
    cliffs_delta,
    cohens_d,
    coverage,
    f1,
    kendall_tau,
    mae,
    matthews_corrcoef,
    mse,
    rmse,
    topk_accuracy,
)
from wca_bench.evaluation.protocol import RollingWindowProtocol, assert_no_leakage
from wca_bench.evaluation.significance import bootstrap_ci, friedman_nemenyi, paired_t_test
from wca_bench.evaluation.stratified import stratified_report

__all__ = [
    "RollingWindowProtocol",
    "assert_no_leakage",
    "stratified_report",
    "bootstrap_ci",
    "paired_t_test",
    "friedman_nemenyi",
    "mae",
    "rmse",
    "mse",
    "coverage",
    "calibration_error",
    "kendall_tau",
    "topk_accuracy",
    "brier_score",
    "auc_roc",
    "auc_pr",
    "f1",
    "matthews_corrcoef",
    "cohens_d",
    "cliffs_delta",
]
