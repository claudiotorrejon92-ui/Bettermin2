"""Ensemble predictor combining ML models with physics-based kinetics."""
from __future__ import annotations

from pathlib import Path
import json
from typing import Dict

import pandas as pd
from joblib import load

from physics.simple_kinetics import predict as kinetics_predict

STORAGE_DIR = Path(__file__).resolve().parents[1] / "storage"


def _load_models(route: str):
    cat_path = STORAGE_DIR / f"performance_{route}_catboost.pkl"
    lgb_path = STORAGE_DIR / f"performance_{route}_lgbm.pkl"
    if not cat_path.exists() or not lgb_path.exists():
        raise FileNotFoundError(f"Models for route '{route}' not found. Train them first.")
    cat_model = load(cat_path)
    lgb_model = load(lgb_path)
    return cat_model, lgb_model


def _load_kinetics(route: str) -> Dict[str, float]:
    path = STORAGE_DIR / f"performance_{route}_kinetics.json"
    with open(path) as f:
        return json.load(f)


def predict_performance(route: str, features: Dict[str, float], time: float) -> float:
    """Predict performance using both ML and physics models.

    Parameters
    ----------
    route: str
        Route identifier.
    features: Dict[str, float]
        Feature dictionary for the ML models.
    time: float
        Time value for the kinetics prediction.
    """
    cat_model, lgb_model = _load_models(route)
    params = _load_kinetics(route)

    df = pd.DataFrame([features])
    ml_pred = 0.5 * (cat_model.predict(df)[0] + lgb_model.predict(df)[0])
    phy_pred = kinetics_predict(time, params["k"], params["n"])
    return float((ml_pred + phy_pred) / 2)
