"""Router exposing the model card metadata."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from governance.model_cards import load_model_card

router = APIRouter()


@router.get("/")
def get_model_card():
    """Return the latest model card contents."""
    try:
        return load_model_card()
    except FileNotFoundError as exc:  # pragma: no cover - runtime error propagation
        raise HTTPException(status_code=404, detail=str(exc)) from exc
