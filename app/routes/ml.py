from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from ..ml import predict_process

router = APIRouter()

class PredictionRequest(BaseModel):
    s_sulfuro_pct: Optional[float] = None
    as_ppm: Optional[float] = None

class PredictionResponse(BaseModel):
    score: float
    recommendation: str

@router.post("/predict", response_model=PredictionResponse)
def predict_ml(request: PredictionRequest):
    """
    Endpoint to get ML-based recommendation using sulfide and arsenic data.
    """
    result = predict_process(request.s_sulfuro_pct, request.as_ppm)
    return result
