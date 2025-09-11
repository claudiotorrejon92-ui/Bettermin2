"""Forecast API exposing a GET /forecast endpoint."""
from __future__ import annotations

from fastapi import FastAPI, HTTPException

from ensemble.performance_predictor import predict_performance

app = FastAPI(title="Forecast API")


@app.get("/forecast")
def get_forecast(route: str, feature1: float, feature2: float, time: float):
    """Return performance forecast for a given route and features."""
    if time < 0:
        raise HTTPException(status_code=400, detail="time must be non-negative")

    features = {"feature1": feature1, "feature2": feature2}
    try:
        forecast = predict_performance(route, features, time)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"Required resource not found: {exc}")
    except Exception as exc:  # pragma: no cover - runtime error propagation
        raise HTTPException(status_code=500, detail=str(exc))
    return {"route": route, "forecast": forecast}
