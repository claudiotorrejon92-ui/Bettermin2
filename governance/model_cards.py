"""Utilities for generating and loading simple model cards."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

MODEL_CARD_PATH = Path("model_card.json")


def generate_model_card(
    model_name: str, version: str, metrics: Dict[str, Any], path: Path | str = MODEL_CARD_PATH
) -> Dict[str, Any]:
    """Create a basic model card and persist it as JSON."""
    card = {
        "model_name": model_name,
        "version": version,
        "generated_at": datetime.utcnow().isoformat(),
        "metrics": metrics,
    }
    Path(path).write_text(json.dumps(card, indent=2))
    return card


def load_model_card(path: Path | str = MODEL_CARD_PATH) -> Dict[str, Any]:
    """Load an existing model card from disk."""
    return json.loads(Path(path).read_text())
