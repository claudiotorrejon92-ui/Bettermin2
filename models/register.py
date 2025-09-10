"""Register and promote models to Production in MLflow."""

from __future__ import annotations

import argparse

import mlflow
from mlflow.tracking import MlflowClient


def promote_to_production(run_id: str, artifact_path: str, name: str) -> None:
    """Register a model from a run and promote it to Production."""
    model_uri = f"runs:/{run_id}/{artifact_path}"
    result = mlflow.register_model(model_uri, name)
    client = MlflowClient()
    client.transition_model_version_stage(
        name=name,
        version=result.version,
        stage="Production",
        archive_existing_versions=True,
    )
    print(f"Registered {name} version {result.version} to Production")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Promote an MLflow model version to Production"
    )
    parser.add_argument("run_id", help="Run ID containing the model artifact")
    parser.add_argument(
        "artifact_path", help="Artifact path of the model inside the run"
    )
    parser.add_argument("name", help="Name for the registered model")
    args = parser.parse_args()
    promote_to_production(args.run_id, args.artifact_path, args.name)
