"""Baseline package export (lazy-friendly)."""

__all__ = [
    "history_mean_predict",
    "kde_predict_result",
    "historical_dnf_predict",
    "logistic_dnf_predict",
    "xgb_result_predict",
    "ridge_result_predict",
    "psych_sheet_predict",
    "plackett_luce_scores",
    "kde_simulate_placement",
    "exponential_limit_estimate",
    "did_transfer_matrix",
    "correlation_transfer_matrix",
]


def __getattr__(name: str):
    if name in {
        "history_mean_predict",
    }:
        from wca_bench.baselines.statistical.history_mean import history_mean_predict

        return history_mean_predict
    if name in {"kde_predict_result", "kde_simulate_placement", "psych_sheet_predict", "plackett_luce_scores"}:
        from wca_bench.baselines.statistical import kde, plackett_luce

        return {
            "kde_predict_result": kde.kde_predict_result,
            "kde_simulate_placement": plackett_luce.kde_simulate_placement,
            "psych_sheet_predict": plackett_luce.psych_sheet_predict,
            "plackett_luce_scores": plackett_luce.plackett_luce_scores,
        }[name]
    if name == "historical_dnf_predict":
        from wca_bench.baselines.statistical.dnf_rate import historical_dnf_predict

        return historical_dnf_predict
    if name == "logistic_dnf_predict":
        from wca_bench.baselines.tree.logistic_dnf import logistic_dnf_predict

        return logistic_dnf_predict
    if name == "xgb_result_predict":
        from wca_bench.baselines.tree.xgb_result import xgb_result_predict

        return xgb_result_predict
    if name == "ridge_result_predict":
        from wca_bench.baselines.tree.ridge_result import ridge_result_predict

        return ridge_result_predict
    if name == "exponential_limit_estimate":
        from wca_bench.baselines.statistical.world_record import exponential_limit_estimate

        return exponential_limit_estimate
    if name in {"did_transfer_matrix", "correlation_transfer_matrix"}:
        from wca_bench.baselines.causal.did import correlation_transfer_matrix, did_transfer_matrix

        return {
            "did_transfer_matrix": did_transfer_matrix,
            "correlation_transfer_matrix": correlation_transfer_matrix,
        }[name]
    raise AttributeError(name)
