"""Bayesian baselines package (closed-form, no probabilistic-programming deps)."""

from wca_bench.baselines.bayesian.beta_binomial_dnf import beta_binomial_dnf_predict
from wca_bench.baselines.bayesian.hierarchical_limit import hierarchical_limit_estimate

__all__ = ["beta_binomial_dnf_predict", "hierarchical_limit_estimate"]
