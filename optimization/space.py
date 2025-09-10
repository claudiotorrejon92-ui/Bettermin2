"""Parameter search space and hard constraints for optimization."""
from __future__ import annotations

from typing import Dict, Tuple


def get_search_space() -> Dict[str, Tuple[float, float]]:
    """Return optimization search space bounds.

    Each entry maps a parameter name to a tuple of ``(low, high)`` bounds.
    The space is intentionally simple and can be adapted to real problems.
    """
    return {
        "temperature": (60.0, 120.0),
        "acid_concentration": (0.0, 10.0),
        "extraction_time": (1.0, 8.0),
    }


def is_feasible(params: Dict[str, float]) -> bool:
    """Return ``True`` if a parameter set satisfies all hard constraints.

    The constraints encode domain knowledge that must not be violated.
    For example, acid concentration should not exceed twice the extraction
    time and extreme acid levels are disallowed at low temperature.
    """
    if params["acid_concentration"] > 2 * params["extraction_time"]:
        return False
    if params["temperature"] < 70 and params["acid_concentration"] > 5:
        return False
    return True
