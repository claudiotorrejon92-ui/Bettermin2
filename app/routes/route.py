from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from models.route_classifier import predict
from rules.route_rules import validate_features

router = APIRouter()

class RouteResponse(BaseModel):
    route: int

@router.get("/route", response_model=RouteResponse)
def get_route(icp_fe: float, icp_s: float, pyrite_pct: float, calcite_pct: float,
              s_sulf: float, anc: float, npr: float):
    """Predict processing route based on geochemical metrics."""
    features = {
        "icp_fe": icp_fe,
        "icp_s": icp_s,
        "pyrite_pct": pyrite_pct,
        "calcite_pct": calcite_pct,
        "s_sulf": s_sulf,
        "anc": anc,
        "npr": npr,
    }
    if not validate_features(features):
        raise HTTPException(status_code=400, detail="Invalid input features")
    route = predict(features)
    return {"route": route}
