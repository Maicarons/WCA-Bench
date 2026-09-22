"""Baseline package export (lazy-friendly)."""

from __future__ import annotations

__all__ = [
    "history_mean_predict",
    "kde_predict_result",
    "historical_dnf_predict",
    "logistic_dnf_predict",
    "xgb_result_predict",
    "xgb_dnf_predict",
    "ridge_result_predict",
    "psych_sheet_predict",
    "plackett_luce_scores",
    "kde_simulate_placement",
    "exponential_limit_estimate",
    "changepoint_limit_estimate",
    "hierarchical_limit_estimate",
    "gp_evt_limit_estimate",
    "beta_binomial_dnf_predict",
    "lstm_result_predict",
    "gnn_placement_predict",
    "did_transfer_matrix",
    "correlation_transfer_matrix",
    "iv_transfer_matrix",
    "causal_forest_transfer_matrix",
]


def __getattr__(name: str):
    if name == "history_mean_predict":
        from wca_bench.baselines.statistical.history_mean import history_mean_predict

        return history_mean_predict
    if name in {"kde_predict_result", "kde_simulate_placement", "psych_sheet_predict", "plackett_luce_scores"}:
        from wca_bench.baselines.statistical import plackett_luce

        if name == "kde_predict_result":
            from wca_bench.baselines.statistical.kde import kde_predict_result

            return kde_predict_result
        return {
            "kde_simulate_placement": plackett_luce.kde_simulate_placement,
            "psych_sheet_predict": plackett_luce.psych_sheet_predict,
            "plackett_luce_scores": plackett_luce.plackett_luce_scores,
        }[name]
    if name == "historical_dnf_predict":
        from wca_bench.baselines.statistical.dnf_rate import historical_dnf_predict

        return historical_dnf_predict
    if name == "beta_binomial_dnf_predict":
        from wca_bench.baselines.bayesian.beta_binomial_dnf import beta_binomial_dnf_predict

        return beta_binomial_dnf_predict
    if name == "logistic_dnf_predict":
        from wca_bench.baselines.tree.logistic_dnf import logistic_dnf_predict

        return logistic_dnf_predict
    if name == "xgb_dnf_predict":
        from wca_bench.baselines.tree.xgb_dnf import xgb_dnf_predict

        return xgb_dnf_predict
    if name == "xgb_result_predict":
        from wca_bench.baselines.tree.xgb_result import xgb_result_predict

        return xgb_result_predict
    if name == "ridge_result_predict":
        from wca_bench.baselines.tree.ridge_result import ridge_result_predict

        return ridge_result_predict
    if name == "lstm_result_predict":
        from wca_bench.baselines.deep.lstm_result import lstm_result_predict

        return lstm_result_predict
    if name == "gnn_placement_predict":
        from wca_bench.baselines.graph.gnn_placement import gnn_placement_predict

        return gnn_placement_predict
    if name == "exponential_limit_estimate":
        from wca_bench.baselines.statistical.world_record import exponential_limit_estimate

        return exponential_limit_estimate
    if name == "changepoint_limit_estimate":
        from wca_bench.baselines.statistical.world_record import changepoint_limit_estimate

        return changepoint_limit_estimate
    if name == "hierarchical_limit_estimate":
        from wca_bench.baselines.bayesian.hierarchical_limit import hierarchical_limit_estimate

        return hierarchical_limit_estimate
    if name == "gp_evt_limit_estimate":
        from wca_bench.baselines.statistical.gp_evt_limit import gp_evt_limit_estimate

        return gp_evt_limit_estimate
    if name in {"did_transfer_matrix", "correlation_transfer_matrix", "iv_transfer_matrix", "causal_forest_transfer_matrix"}:
        from wca_bench.baselines.causal import causal_forest, did, iv

        return {
            "did_transfer_matrix": did.did_transfer_matrix,
            "correlation_transfer_matrix": did.correlation_transfer_matrix,
            "iv_transfer_matrix": iv.iv_transfer_matrix,
            "causal_forest_transfer_matrix": causal_forest.causal_forest_transfer_matrix,
        }[name]
    raise AttributeError(name)
