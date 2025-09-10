"""API exposing endpoints for logging runs and outcomes."""
from __future__ import annotations

from typing import Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from active_learning.scheduler import Scheduler


app = FastAPI(title="Runs API")


# Instantiate scheduler with simple heuristics similar to active learning module
scheduler = Scheduler(lambda f: (0.0, 1.0), lambda f: 0.5)


class RunRequest(BaseModel):
    features: Dict[str, float]


class RunResponse(BaseModel):
    run_id: int


@app.post("/runs", response_model=RunResponse)
def create_run(req: RunRequest):
    """Register a new run and return its identifier."""
    run_id = scheduler.register_run(req.features)
    return {"run_id": run_id}


class OutcomeRequest(BaseModel):
    run_id: int
    outcome: float


@app.post("/outcomes")
def create_outcome(req: OutcomeRequest):
    """Register outcome for a run and trigger model retraining."""
    try:
        scheduler.register_outcome(req.run_id, req.outcome)
    except IndexError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"status": "ok"}
