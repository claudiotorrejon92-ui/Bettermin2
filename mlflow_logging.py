"""Utilities for logging metrics and artifacts to MLflow."""
from __future__ import annotations

from typing import Dict, Optional, Any

import mlflow


def log_run(
    run_name: str,
    metrics: Dict[str, float],
    artifacts: Dict[str, str],
    params: Optional[Dict[str, Any]] = None,
) -> str:
    """Log metrics and artifacts to MLflow.

    Parameters
    ----------
    run_name:
        Name assigned to the MLflow run.
    metrics:
        Dictionary of metric names to values.
    artifacts:
        Dictionary mapping artifact names to file paths.
    params:
        Optional dictionary of parameters to log.

    Returns
    -------
    str
        The MLflow run identifier.
    """
    with mlflow.start_run(run_name=run_name) as run:
        if params:
            mlflow.log_params(params)
        if metrics:
            mlflow.log_metrics(metrics)
        for name, path in artifacts.items():
            mlflow.log_artifact(path, artifact_path=name)
        return run.info.run_id
