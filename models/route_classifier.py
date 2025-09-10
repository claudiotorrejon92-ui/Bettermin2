"""Decision tree classifier for processing route prediction."""

from pathlib import Path
from typing import Dict

import mlflow
import pandas as pd
from joblib import dump, load
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.tree import DecisionTreeClassifier

from mlflow_logging import log_run
from rules.route_rules import validate_features

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "route" / "training_data.csv"
MODEL_PATH = Path(__file__).resolve().parents[1] / "storage" / "route_model.pkl"


def train() -> Dict[str, object]:
    """Train the decision tree model and evaluate its performance.

    Returns a dict with accuracy, confusion matrix and penalized accuracy that
    subtracts a penalty for false negatives in critical samples.
    """
    df = pd.read_csv(DATA_PATH)
    df = df[df.apply(lambda r: validate_features(r.to_dict()), axis=1)]

    X = df.drop(columns=["critical"])
    y = df["critical"]

    clf = DecisionTreeClassifier(random_state=42)
    clf.fit(X, y)

    preds = clf.predict(X)
    acc = accuracy_score(y, preds)
    cm = confusion_matrix(y, preds)
    fn = cm[1][0]
    penalized_acc = acc - 0.1 * fn

    dump(clf, MODEL_PATH)

    metrics = {"accuracy": acc, "penalized_accuracy": penalized_acc}
    artifacts = {"model": str(MODEL_PATH)}
    run_id = log_run("route_classifier", metrics, artifacts)
    with mlflow.start_run(run_id=run_id):
        mlflow.set_tags({"route": "route_classifier", "version": "1"})
        mlflow.sklearn.log_model(
            clf,
            "route_classifier_model",
            registered_model_name="route_classifier",
        )

    return {
        "accuracy": acc,
        "confusion_matrix": cm.tolist(),
        "penalized_accuracy": penalized_acc,
    }


def predict(features: Dict[str, float]) -> int:
    """Predict processing route for given features."""
    if not validate_features(features):
        raise ValueError("Invalid features for prediction")
    if not MODEL_PATH.exists():
        train()
    model = load(MODEL_PATH)
    df = pd.DataFrame([features])
    prediction = model.predict(df)[0]
    return int(prediction)


if __name__ == "__main__":
    metrics = train()
    print(metrics)
