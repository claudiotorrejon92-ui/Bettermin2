"""Endpoints exposing forecasting functionality via the shared API app."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ensemble.performance_predictor import predict_performance

router = APIRouter()


class ForecastResponse(BaseModel):
    """Response model for the forecast endpoint."""

    route: str
    forecast: float


@router.get("/", response_model=ForecastResponse)
def get_forecast(route: str, feature1: float, feature2: float, time: float) -> ForecastResponse:
    """Return the performance forecast for the provided route and features."""
    if time < 0:
        raise HTTPException(status_code=400, detail="time must be non-negative")

    features = {"feature1": feature1, "feature2": feature2}

    try:
        forecast = predict_performance(route, features, time)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404, detail=f"Required resource not found: {exc}"
        ) from exc
    except Exception as exc:  # pragma: no cover - runtime error propagation
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return ForecastResponse(route=route, forecast=float(forecast))
