"""
FastAPI ingestion service with unit validation and outlier detection.

This module exposes a minimal API for ingesting measurement data while
checking that units are valid and values are not statistical outliers.
"""

from pathlib import Path
import os
from typing import List, Literal, Optional

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator

from storage.feature_store import (
    DuckDBFeatureStore,
    PostgresFeatureStore,
    SheetsFeatureStore,
)

# Supported units and conversion factors to kilograms
UNIT_FACTORS = {"kg": 1.0, "g": 1e-3, "mg": 1e-6}

# Configure feature store backend
BACKEND = os.getenv("FEATURE_STORE_BACKEND", "duckdb")
if BACKEND == "duckdb":
    FEATURE_STORE = DuckDBFeatureStore()
elif BACKEND == "postgres":
    conn_str = os.getenv("POSTGRES_DSN", "postgresql://postgres:postgres@localhost/postgres")
    FEATURE_STORE = PostgresFeatureStore(conn_str)
elif BACKEND == "sheets":
    creds_file = Path(os.getenv("GOOGLE_SHEETS_CREDS", "creds.json"))
    sheet_name = os.getenv("GOOGLE_SHEETS_SPREADSHEET", "FeatureStore")
    FEATURE_STORE = SheetsFeatureStore(creds_file, sheet_name)
else:
    raise ValueError(f"Unsupported feature store backend: {BACKEND}")


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
    df = pd.DataFrame([m.dict() for m in data])
    FEATURE_STORE.save_table(df, "measurements")
    return {"count": len(data), "values_kg": [m.to_kg() for m in data]}


@app.on_event("shutdown")
def shutdown_event() -> None:
    """Close feature store connections on shutdown."""
    FEATURE_STORE.close()
