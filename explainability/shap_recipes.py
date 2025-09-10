"""Utility to compute SHAP values for optimisation recommendations."""
from __future__ import annotations

from typing import Dict, Callable


def shap_for_recommendation(objective_fn: Callable[[Dict[str, float]], float],
                            params: Dict[str, float]) -> Dict[str, float]:
    """Return SHAP values explaining the recommendation.

    The function uses SHAP's :class:`KernelExplainer` on the provided
    ``objective_fn``. If the ``shap`` package is not installed an empty
    dictionary is returned instead of raising an ImportError, allowing the
    caller to degrade gracefully.
    """
    try:  # pragma: no cover - optional dependency
        import shap
        import numpy as np
    except Exception:  # pragma: no cover - shap not installed
        return {}

    keys = list(params.keys())
    x = np.array([list(params.values())])

    def _wrapped(x_arr):
        return [objective_fn(dict(zip(keys, row))) for row in x_arr]

    explainer = shap.KernelExplainer(_wrapped, x)
    shap_values = explainer.shap_values(x)[0]
    return {k: float(v) for k, v in zip(keys, shap_values)}
