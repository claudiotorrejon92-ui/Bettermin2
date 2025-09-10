"""API exposing a GET /modelcard endpoint."""
from __future__ import annotations

from fastapi import FastAPI, HTTPException

from governance.model_cards import load_model_card

app = FastAPI(title="Model Card API")


@app.get("/modelcard")
def get_model_card():
    """Return the latest model card."""
    try:
        card = load_model_card()
    except FileNotFoundError as exc:  # pragma: no cover - runtime error propagation
        raise HTTPException(status_code=404, detail=str(exc))
    return card
