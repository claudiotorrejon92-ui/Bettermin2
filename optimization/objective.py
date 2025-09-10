"""Composite objective function combining extraction, acid usage and arsenic."""
from __future__ import annotations

from typing import Dict


def _combine_metrics(extraction: float, acid: float, arsenic: float) -> float:
    """Combine individual metrics into a single score.

    Extraction is maximised while acid consumption and arsenic content are
    penalised. Coefficients are illustrative and can be tuned.
    """
    return extraction - 0.5 * acid - 0.2 * arsenic


def objective(params: Dict[str, float]) -> float:
    """Toy objective using the optimisation parameters.

    In a real scenario this function would evaluate laboratory experiments or
    a surrogate ML model. For testing purposes we derive simple proxies for
    extraction, acid consumption and arsenic from the input parameters.
    """
    temperature = params["temperature"]
    acid_conc = params["acid_concentration"]
    time = params["extraction_time"]

    extraction = 0.8 * temperature - 0.3 * acid_conc - 2 * time
    acid = acid_conc
    arsenic = 0.1 * temperature + 0.4 * time
    return _combine_metrics(extraction, acid, arsenic)
