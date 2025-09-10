"""Training utilities for performance models using quantile regression."""
from __future__ import annotations

from pathlib import Path
import json
from typing import Dict

import pandas as pd
from joblib import dump

from physics.simple_kinetics import fit_rate


DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "performance"
STORAGE_DIR = Path(__file__).resolve().parents[1] / "storage"


def _load_dataset(route: str) -> pd.DataFrame:
    path = DATA_DIR / route / "train.csv"
    if not path.exists():
        raise FileNotFoundError(f"Dataset for route '{route}' not found at {path}")
    return pd.read_csv(path)


def train_route(route: str) -> Dict[str, float]:
    """Train CatBoost and LightGBM quantile regressors for a route.

    The trained models are stored in ``storage`` and the fitted kinetics
    parameters ``k`` and ``n`` are returned as a dictionary.
    """
    df = _load_dataset(route)
    X = df[["feature1", "feature2"]]
    y = df["performance"]

    from catboost import CatBoostRegressor  # Lazy import
    from lightgbm import LGBMRegressor

    cat_model = CatBoostRegressor(loss_function="Quantile:alpha=0.5", verbose=False)
    cat_model.fit(X, y)

    lgb_model = LGBMRegressor(objective="quantile", alpha=0.5)
    lgb_model.fit(X, y)

    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    dump(cat_model, STORAGE_DIR / f"performance_{route}_catboost.pkl")
    dump(lgb_model, STORAGE_DIR / f"performance_{route}_lgbm.pkl")

    k, n = fit_rate(df["time"].to_numpy(), df["performance"].to_numpy())
    with open(STORAGE_DIR / f"performance_{route}_kinetics.json", "w") as f:
        json.dump({"k": k, "n": n}, f)

    return {"k": k, "n": n}


def train_all() -> Dict[str, Dict[str, float]]:
    """Train models for all available routes."""
    metrics = {}
    for route_dir in DATA_DIR.iterdir():
        if route_dir.is_dir():
            route = route_dir.name
            metrics[route] = train_route(route)
    return metrics


if __name__ == "__main__":  # pragma: no cover
    print(train_all())
