from typing import Dict, Any


def predict_bio_process(s_sulfuro_pct: float, as_ppm: float) -> Dict[str, str]:
    """
    Predicts the recommended bio-process given geochemical parameters.
    This is a placeholder for a more sophisticated ML model.
    """
    # Handle missing data
    if s_sulfuro_pct is None:
        return {"recommendation": "Sin datos de S_sulfuro"}
    # BIOX recommended
    if s_sulfuro_pct > 1 and (as_ppm is None or as_ppm < 500):
        return {"recommendation": "BIOX"}
    # High arsenic risk -> consider biolixiviación.
    # Business rule: only values above 500 ppm trigger this path; 500 ppm is treated
    # as a borderline case and falls through to the default recommendation.
    if as_ppm is not None and as_ppm > 500:
        return {"recommendation": "Biolixiviación"}
    # Default case: preconcentración o biolixiviación
    return {"recommendation": "Preconcentración o biolixiviación"}


def extract_features(lab_data: Dict[str, Any]) -> Dict[str, float]:
    """
    Example feature extraction for lab data. This can be extended to include
    complex bioinformatic pipelines (e.g. 16S profiling, shotgun metagenomics).
    For now it just maps common column names to features used by the model.
    """
    features: Dict[str, float] = {}
    # Map common keys to standardized feature names
    if 'S_sulfuro_%' in lab_data:
        features['s_sulfuro_pct'] = float(lab_data['S_sulfuro_%'])
    if 'As_ppm' in lab_data:
        features['as_ppm'] = float(lab_data['As_ppm'])
    # Additional processing could be added here
    return features
