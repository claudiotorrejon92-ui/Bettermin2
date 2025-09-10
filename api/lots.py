"""API exposing minimal endpoints for lot operations."""
from __future__ import annotations

from fastapi import FastAPI, HTTPException

app = FastAPI(title="Lots API")

# In-memory placeholder store; replace with database in real deployment.
_FAKE_LOTS = [
    {"lote_id": "L1", "description": "Sample lot"},
    {"lote_id": "L2", "description": "Another lot"},
]


@app.get("/lots")
def list_lots():
    """Return the available lots."""
    return _FAKE_LOTS


@app.get("/lots/{lote_id}")
def get_lot(lote_id: str):
    """Return details for a specific lot."""
    for lot in _FAKE_LOTS:
        if lot["lote_id"] == lote_id:
            return lot
    raise HTTPException(status_code=404, detail="Lot not found")
