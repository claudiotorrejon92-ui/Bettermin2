"""Active learning scheduler using EI or UCB with safety constraints."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Tuple
from math import erf, exp, sqrt, pi

try:  # Lazy import so the scheduler works without the pipeline
    from pipelines.retrain import run as _default_retrain
except Exception:  # pragma: no cover - pipeline may not be available
    _default_retrain = None


# ----------------------------------------------------------------------------
# Helper functions for normal distribution
# ----------------------------------------------------------------------------

def _norm_pdf(x: float) -> float:
    return (1.0 / sqrt(2.0 * pi)) * exp(-0.5 * x * x)


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


# ----------------------------------------------------------------------------
# Scheduler definition
# ----------------------------------------------------------------------------

BenefitPredictor = Callable[[Dict[str, float]], Tuple[float, float]]
SafetyPredictor = Callable[[Dict[str, float]], float]
RetrainCallback = Callable[[List[Dict[str, float]]], None]


@dataclass
class Scheduler:
    """Select experiments balancing exploration and safety.

    Parameters
    ----------
    benefit_predictor:
        Callable returning ``(mean, std)`` for the expected benefit of a set of
        features.
    safety_predictor:
        Callable returning the probability of a configuration being safe.
    strategy:
        Either ``"ei"`` for expected improvement or ``"ucb"`` for upper
        confidence bound.
    kappa:
        Exploration parameter for the UCB strategy.
    xi:
        Small positive value encouraging exploration for EI.
    retrain_callback:
        Optional callable invoked when a number of outcomes has been
        registered, allowing model retraining to be triggered. By default this
        points to ``pipelines.retrain.run`` if available.
    retrain_every:
        Trigger ``retrain_callback`` after this many completed runs. A value of
        ``0`` disables automatic retraining.
    """

    benefit_predictor: BenefitPredictor
    safety_predictor: SafetyPredictor
    strategy: str = "ei"
    kappa: float = 2.0
    xi: float = 0.01
    retrain_callback: Optional[RetrainCallback] = _default_retrain
    retrain_every: int = 0
    history: List[Dict[str, float]] = field(default_factory=list)
    best_observed: float = float("-inf")

    # ------------------------------------------------------------------
    # Scoring utilities
    # ------------------------------------------------------------------
    def _expected_improvement(self, mean: float, std: float) -> float:
        if std <= 0:
            improvement = mean - self.best_observed - self.xi
            return max(improvement, 0.0)
        improvement = mean - self.best_observed - self.xi
        z = improvement / std
        return improvement * _norm_cdf(z) + std * _norm_pdf(z)

    def _ucb(self, mean: float, std: float) -> float:
        return mean + self.kappa * std

    def _base_score(self, mean: float, std: float) -> float:
        if self.strategy == "ucb":
            return self._ucb(mean, std)
        return self._expected_improvement(mean, std)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def score(self, features: Dict[str, float]) -> float:
        """Return acquisition score for a set of features."""
        mean, std = self.benefit_predictor(features)
        p_safe = self.safety_predictor(features)
        return p_safe * self._base_score(mean, std)

    def suggest(self, candidates: Iterable[Dict[str, float]]) -> Dict[str, float]:
        """Return the best candidate according to the acquisition function."""
        best_candidate = None
        best_score = float("-inf")
        for cand in candidates:
            score = self.score(cand)
            if score > best_score:
                best_score = score
                best_candidate = cand
        if best_candidate is None:
            raise ValueError("No candidates provided")
        return best_candidate

    def register_run(self, features: Dict[str, float]) -> int:
        """Log a run and return its identifier."""
        self.history.append({"features": features})
        return len(self.history) - 1

    def register_outcome(self, run_id: int, outcome: float) -> None:
        """Associate an outcome with a run and trigger retraining if needed."""
        if run_id < 0 or run_id >= len(self.history):
            raise IndexError("Run ID out of range")
        self.history[run_id]["outcome"] = outcome
        if outcome > self.best_observed:
            self.best_observed = outcome
        if (
            self.retrain_callback is not None
            and self.retrain_every > 0
            and sum(1 for h in self.history if "outcome" in h) % self.retrain_every == 0
        ):
            self.retrain_callback(self.history)
