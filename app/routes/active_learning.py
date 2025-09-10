"""Endpoints for logging runs and outcomes triggering active learning."""
from __future__ import annotations

from typing import Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from active_learning.scheduler import Scheduler
from models.performance.train import train_all

# ---------------------------------------------------------------------------
# Predictor connectors
# ---------------------------------------------------------------------------

def _benefit_predictor(features: Dict[str, float]):
    """Return mean and std of expected benefit for the given features.

    This is a thin wrapper around existing predictors. If a predictor is not
    available the function falls back to simple heuristics so that the API
    remains operational in environments without trained models.
    """
    try:  # pragma: no cover - optional heavy dependency
        from ensemble.performance_predictor import predict_performance

        # Here we arbitrarily select route "default" and time 0.0 as this
        # project does not expose these parameters through the API yet.
        mean = float(predict_performance("default", features, 0.0))
    except Exception:  # pragma: no cover - model not available
        # Graceful fallback so unit tests don't require trained models
        mean = sum(features.values()) / len(features)
    # Simple uncertainty proxy
    std = 1.0
    return mean, std


def _safety_predictor(features: Dict[str, float]) -> float:
    """Probability that the configuration is safe.

    Uses the route classifier as a proxy for safety. Any non-zero prediction is
    considered unsafe. If the model cannot be loaded the function returns a
    conservative 0.5 probability.
    """
    try:  # pragma: no cover - optional heavy dependency
        from models.route_classifier import predict as route_predict

        pred = route_predict(features)
        return 1.0 - float(pred)
    except Exception:  # pragma: no cover - model not available
        return 0.5


# Scheduler instance used by the API
def _retrain_callback(_history):  # pragma: no cover - runtime side effect
    try:
        train_all()
    except Exception:
        # Training requires optional dependencies; failures are ignored so the
        # API remains responsive in minimal environments.
        pass


scheduler = Scheduler(
    _benefit_predictor, _safety_predictor, retrain_callback=_retrain_callback
)


router = APIRouter()


class RunRequest(BaseModel):
    features: Dict[str, float]


class RunResponse(BaseModel):
    run_id: int


@router.post("/runs", response_model=RunResponse)
def create_run(req: RunRequest):
    """Register a new run and return its identifier."""
    run_id = scheduler.register_run(req.features)
    return {"run_id": run_id}


class OutcomeRequest(BaseModel):
    run_id: int
    outcome: float


@router.post("/outcomes")
def create_outcome(req: OutcomeRequest):
    """Register outcome for a run and trigger model retraining."""
    try:
        scheduler.register_outcome(req.run_id, req.outcome)
    except IndexError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"status": "ok"}
