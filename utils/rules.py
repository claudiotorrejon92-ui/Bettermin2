"""
Simple business rules for Eco‑Pilot Caracterización.

This module implements a basic rule engine that recommends a processing route
based on sulfide content and arsenic levels.  In una producción real se
debería reemplazar o extender con un motor de reglas más sofisticado o un
modelo de machine learning.
"""

from typing import Optional


def recommend_process(s_sulfuro_pct: Optional[float], as_ppm: Optional[float]) -> str:
    """Devuelve una recomendación de proceso en función de la geoquímica.

    - Si `s_sulfuro_pct` es mayor que 1 % y `as_ppm` es nulo o menor a 500 ppm,
      se recomienda un proceso de oxidación biológica (BIOX).
    - Si `as_ppm` es mayor a 500 ppm se sugiere analizar riesgos de arsénico y
      considerar biolixiviación.
    - En cualquier otro caso se recomienda preconcentración o biolixiviación.

    :param s_sulfuro_pct: Porcentaje de azufre en fase sulfuro (0–100)
    :param as_ppm: Contenido de arsénico en partes por millón
    :return: Cadena con la recomendación (“BIOX”, “Revisar arsénico”, etc.)
    """
    if s_sulfuro_pct is None:
        return "Sin datos de S_sulfuro"

    # BIOX recomendado
    if s_sulfuro_pct > 1 and (as_ppm is None or as_ppm < 500):
        return "BIOX"

    # Riesgo de arsénico elevado
    if as_ppm is not None and as_ppm > 500:
        return "Revisar riesgo de arsénico y considerar biolixiviación"

    # Otra alternativa
    return "Preconcentración o biolixiviación"
