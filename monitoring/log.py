from __future__ import annotations

"""Utility for logging prediction outcomes for monitoring."""

from pathlib import Path
import csv
import json
from datetime import datetime
from typing import Any, Dict, Optional

# Path to the structured log file
LOG_FILE = Path(__file__).with_name("predictions_log.csv")

# Columns stored in the log
FIELDNAMES = [
    "timestamp",
    "batch",
    "input",
    "prediction",
    "outcome",
    "improvement",
]


def log_event(
    input_data: Dict[str, Any],
    prediction: float,
    outcome: Optional[float] = None,
    improvement: Optional[float] = None,
    batch: Optional[str] = None,
) -> None:
    """Append a prediction event to the structured log.

    Parameters
    ----------
    input_data: dict
        Features sent to the model.
    prediction: float
        Model prediction.
    outcome: float, optional
        Real outcome observed. If provided and ``improvement`` is not
        specified, the improvement is computed as ``outcome - prediction``.
    improvement: float, optional
        Uplift obtained from the prediction.
    batch: str, optional
        Identifier for the batch or lot.
    """

    if improvement is None and outcome is not None:
        improvement = outcome - prediction

    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "batch": batch,
        "input": json.dumps(input_data, sort_keys=True),
        "prediction": prediction,
        "outcome": outcome,
        "improvement": improvement,
    }

    exists = LOG_FILE.exists()
    with LOG_FILE.open("a", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        if not exists:
            writer.writeheader()
        writer.writerow(record)
