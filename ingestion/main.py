"""
FastAPI ingestion service with unit validation and outlier detection.

This module exposes a minimal API for ingesting measurement data while
checking that units are valid and values are not statistical outliers.
"""

from typing import List, Literal, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator

# Supported units and conversion factors to kilograms
UNIT_FACTORS = {"kg": 1.0, "g": 1e-3, "mg": 1e-6}


class Measurement(BaseModel):
    """A single measurement with optional statistical context."""

    name: str
    value: float
    unit: Literal["kg", "g", "mg"]
    mean: Optional[float] = None
    std: Optional[float] = None

    @validator("value")
    def check_outlier(cls, v, values):
        """Simple z‑score based outlier detection."""
        mean = values.get("mean")
        std = values.get("std")
        if mean is not None and std is not None and std > 0:
            z = abs(v - mean) / std
            if z > 3:
                raise ValueError(f"value {v} is an outlier (z={z:.2f})")
        return v

    def to_kg(self) -> float:
        """Return the measurement converted to kilograms."""
        factor = UNIT_FACTORS.get(self.unit)
        if factor is None:
            raise ValueError(f"Unsupported unit: {self.unit}")
        return self.value * factor


app = FastAPI(title="Ingestion API")


@app.post("/ingest")
def ingest(data: List[Measurement]):
    """Ingest a batch of measurements ensuring unit validity."""
    for m in data:
        if m.unit not in UNIT_FACTORS:
            raise HTTPException(status_code=400, detail=f"Unsupported unit: {m.unit}")
    # Return count and values in base units for confirmation
    return {"count": len(data), "values_kg": [m.to_kg() for m in data]}
