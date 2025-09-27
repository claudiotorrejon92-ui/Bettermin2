"""Router providing optimisation recommendations."""
from __future__ import annotations

from typing import Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from explainability.shap_recipes import shap_for_recommendation
from optimization.bayes_opt import optimize
from optimization.objective import objective

router = APIRouter()


class RecommendationResponse(BaseModel):
    """Response model containing optimisation results."""

    params: Dict[str, float]
    score: float
    shap: Dict[str, float]


@router.get("/", response_model=RecommendationResponse)
def get_recommendations(n_trials: int = 50) -> RecommendationResponse:
    """Return recommended parameters and SHAP explanations."""
    if n_trials <= 0:
        raise HTTPException(status_code=400, detail="n_trials must be positive")

    try:
        study = optimize(n_trials=n_trials)
    except Exception as exc:  # pragma: no cover - runtime failures
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    params = getattr(study, "best_params", None)
    score = getattr(study, "best_value", None)
    if not params or score is None:
        raise HTTPException(status_code=404, detail="No feasible recommendations found")

    try:
        shap_values = shap_for_recommendation(objective, params)
    except Exception as exc:  # pragma: no cover - shap optional dependency
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return RecommendationResponse(
        params={k: float(v) for k, v in params.items()},
        score=float(score),
        shap={k: float(v) for k, v in shap_values.items()},
    )
