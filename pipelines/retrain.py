"""Pipeline to retrain models using data from the feature store."""
from __future__ import annotations

from pathlib import Path
from typing import Dict

import duckdb
from mlflow_logging import log_run
from models import route_classifier
from models.performance.train import train_all as train_performance

FEATURE_STORE_PATH = Path("storage/feature_store.duckdb")
STORAGE_DIR = Path("storage")


def _load_feature_tables() -> Dict[str, "pd.DataFrame"]:
    """Load all tables from the feature store as pandas DataFrames."""
    import pandas as pd  # imported lazily

    if not FEATURE_STORE_PATH.exists():
        return {}
    con = duckdb.connect(str(FEATURE_STORE_PATH))
    try:
        tables = con.execute("SHOW TABLES").df()["name"].tolist()
        return {name: con.execute(f"SELECT * FROM {name}").df() for name in tables}
    finally:
        con.close()


def run() -> None:
    """Execute retraining of all models and log metrics and artifacts."""
    _load_feature_tables()

    route_metrics = route_classifier.train()
    perf_metrics = train_performance()

    metrics = {f"route_{k}": v for k, v in route_metrics.items()}
    for route, vals in perf_metrics.items():
        for key, value in vals.items():
            metrics[f"{route}_{key}"] = value

    artifacts = {
        "route_model": str(STORAGE_DIR / "route_model.pkl"),
        "performance_models": str(STORAGE_DIR),
    }
    log_run("retrain", metrics, artifacts)


if __name__ == "__main__":  # pragma: no cover
    run()
