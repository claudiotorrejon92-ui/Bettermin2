from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from ..lab_pipeline import predict_bio_process

router = APIRouter()

class LabPredictionRequest(BaseModel):
    s_sulfuro_pct: Optional[float] = None
    as_ppm: Optional[float] = None

class LabPredictionResponse(BaseModel):
    recommendation: str

@router.post("/predict", response_model=LabPredictionResponse)
async def predict_lab(req: LabPredictionRequest):
    """Predicts the recommended bio-process using lab features."""
    result = predict_bio_process(req.s_sulfuro_pct, req.as_ppm)
    return LabPredictionResponse(recommendation=result["recommendation"])
