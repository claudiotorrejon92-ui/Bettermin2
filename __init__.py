"""
Utility functions and rule engine for Eco‑Pilot Caracterización.

This package currently includes a simple rule evaluator used in the Streamlit
front‑end to recommend a processing route (p. ej. BIOX, preconcentración o
biolixiviación) en función de la geoquímica promedio.
"""

from .rules import recommend_process  # noqa: F401

__all__ = ["recommend_process"]