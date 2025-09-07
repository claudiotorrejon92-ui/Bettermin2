import math
from typing import Optional


def predict_process(s_sulfuro_pct: Optional[float], as_ppm: Optional[float]) -> dict:
    """
    Predict processing recommendation based on sulfide and arsenic levels using a simple logistic model.
    :param s_sulfuro_pct: sulfide content (%) of sulfur
    :param as_ppm: arsenic content (ppm)
    :return: a dict with a score between 0 and 1 and a recommendation string.
    """
    s = s_sulfuro_pct if s_sulfuro_pct is not None else 0.0
    arsenic = as_ppm if as_ppm is not None else 0.0
    # simple logistic model: negative intercept plus positive weight on sulfides and negative weight on arsenic
    z = -2.0 + 1.5 * s - 0.003 * arsenic
    score = 1 / (1 + math.exp(-z))
    recommendation = "BIOX" if score > 0.5 else "Preconcentración o biolixiviación"
    return {"score": score, "recommendation": recommendation}
