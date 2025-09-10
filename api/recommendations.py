"""API exposing a GET /recommendations endpoint."""
from __future__ import annotations

from fastapi import FastAPI, HTTPException

from optimization.bayes_opt import optimize
from optimization.objective import objective
from explainability.shap_recipes import shap_for_recommendation

app = FastAPI(title="Recommendation API")


@app.get("/recommendations")
def get_recommendations(n_trials: int = 50):
    """Return recommended parameters and SHAP explanations."""
    try:
        study = optimize(n_trials=n_trials)
        params = study.best_params
        score = study.best_value
        shap_values = shap_for_recommendation(objective, params)
    except Exception as exc:  # pragma: no cover - runtime failures
        raise HTTPException(status_code=400, detail=str(exc))
    return {"params": params, "score": score, "shap": shap_values}
