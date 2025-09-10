"""Bayesian optimisation wrapper using Optuna when available."""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict

from .objective import objective
from .space import get_search_space, is_feasible

try:  # pragma: no cover - optional dependency
    import optuna
except Exception:  # pragma: no cover - optuna not installed
    optuna = None


@dataclass
class SimpleStudy:
    """Fallback study object mimicking Optuna's interface."""
    best_params: Dict[str, float]
    best_value: float


def optimize(n_trials: int = 50):
    """Optimise the objective returning a study-like object.

    If Optuna is available it is used to sample the space. Otherwise a very
    basic random search is performed so that the system remains functional in
    environments without the dependency installed.
    """
    space = get_search_space()

    if optuna is not None:
        def _obj(trial: "optuna.Trial") -> float:
            params = {
                name: trial.suggest_float(name, low, high)
                for name, (low, high) in space.items()
            }
            if not is_feasible(params):
                raise optuna.TrialPruned()
            return objective(params)

        study = optuna.create_study(direction="maximize")
        study.optimize(_obj, n_trials=n_trials)
        return study

    # Fallback random search
    best_params = None
    best_value = float("-inf")
    for _ in range(n_trials):
        params = {k: random.uniform(low, high) for k, (low, high) in space.items()}
        if not is_feasible(params):
            continue
        value = objective(params)
        if value > best_value:
            best_value = value
            best_params = params
    return SimpleStudy(best_params, best_value)
