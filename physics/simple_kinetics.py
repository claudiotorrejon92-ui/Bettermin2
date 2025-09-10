"""Simple kinetics module to fit and predict reaction rates.

This module models a rate equation ``y = k * t**n`` and provides utilities
for fitting the parameters ``k`` and ``n`` using non-linear regression as
well as making predictions given time values.
"""
from __future__ import annotations

from typing import Iterable, Tuple

import numpy as np


def _rate_equation(t: np.ndarray, k: float, n: float) -> np.ndarray:
    """Power-law rate equation ``y = k * t**n``.

    Parameters
    ----------
    t: np.ndarray
        Array of time values.
    k: float
        Rate constant.
    n: float
        Reaction order.
    """
    return k * np.power(t, n)


def fit_rate(time: Iterable[float], conversion: Iterable[float]) -> Tuple[float, float]:
    """Fit the power-law kinetics model to data.

    Parameters
    ----------
    time: Iterable[float]
        Sequence of time measurements.
    conversion: Iterable[float]
        Sequence of observed conversion values.

    Returns
    -------
    Tuple[float, float]
        Estimated ``k`` and ``n`` parameters.
    """
    from scipy.optimize import curve_fit  # Imported lazily to keep optional

    t = np.asarray(list(time), dtype=float)
    y = np.asarray(list(conversion), dtype=float)
    popt, _ = curve_fit(_rate_equation, t, y, bounds=(0, np.inf))
    k, n = popt
    return float(k), float(n)


def predict(time: Iterable[float] | float, k: float, n: float) -> np.ndarray:
    """Predict conversion values using fitted parameters.

    Parameters
    ----------
    time: Iterable[float] | float
        Time value or iterable of time values.
    k: float
        Rate constant.
    n: float
        Reaction order.

    Returns
    -------
    np.ndarray
        Predicted conversion values.
    """
    t = np.asarray(time, dtype=float)
    return _rate_equation(t, k, n)
