"""Simple model serving using ONNX Runtime or native LightGBM."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Callable, Optional

import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from monitoring.log import log_event

try:  # Optional dependency
    import onnxruntime as ort
except Exception:  # pragma: no cover - optional
    ort = None

try:  # Optional dependency
    import lightgbm as lgb
except Exception:  # pragma: no cover - optional
    lgb = None


class PredictRequest(BaseModel):
    features: Dict[str, float]
    batch: Optional[str] = None
    outcome: Optional[float] = None
    improvement: Optional[float] = None


def _load_predictor(model_path: Path) -> Callable[[Dict[str, float]], float]:
    """Load a predictor function for the given model path."""
    if model_path.suffix == ".onnx" and ort is not None:
        session = ort.InferenceSession(str(model_path))
        input_name = session.get_inputs()[0].name

        def _predict(features: Dict[str, float]) -> float:
            arr = np.array([[features[k] for k in sorted(features)]], dtype=np.float32)
            return float(session.run(None, {input_name: arr})[0][0])

        return _predict
    if model_path.suffix in {".txt", ".lgb", ".pkl"} and lgb is not None:
        booster = lgb.Booster(model_file=str(model_path))

        def _predict(features: Dict[str, float]) -> float:
            arr = np.array([[features[k] for k in sorted(features)]])
            return float(booster.predict(arr)[0])

        return _predict
    raise ValueError("Unsupported model format or missing dependency")


def create_app(model_path: str) -> FastAPI:
    """Create a FastAPI app serving predictions for the given model."""
    predictor = _load_predictor(Path(model_path))
    app = FastAPI(title="Inference API")

    @app.post("/predict")
    def predict(req: PredictRequest):
        try:
            result = predictor(req.features)
        except Exception as exc:  # pragma: no cover - runtime errors
            raise HTTPException(status_code=400, detail=str(exc))
        log_event(
            input_data=req.features,
            prediction=result,
            outcome=req.outcome,
            improvement=req.improvement,
            batch=req.batch,
        )
        return {"prediction": result}

    return app


if __name__ == "__main__":  # pragma: no cover
    import argparse
    import uvicorn

    parser = argparse.ArgumentParser(description="Serve a model for inference")
    parser.add_argument("model_path", type=str, help="Path to ONNX or LightGBM model")
    args = parser.parse_args()

    app = create_app(args.model_path)
    uvicorn.run(app, host="0.0.0.0", port=8000)
