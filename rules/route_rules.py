"""Pre-check rules for route classification."""
from typing import Dict

REQUIRED_FIELDS = [
    "icp_fe",
    "icp_s",
    "pyrite_pct",
    "calcite_pct",
    "s_sulf",
    "anc",
    "npr",
]

def validate_features(features: Dict[str, float]) -> bool:
    """Validate input features for the route classifier.

    Ensures all required fields are present and that key metrics are non-negative
    with a positive neutralization potential ratio (NPR).
    """
    for field in REQUIRED_FIELDS:
        value = features.get(field)
        if value is None:
            return False
        if field in {"s_sulf", "anc", "icp_fe", "icp_s", "pyrite_pct", "calcite_pct"} and value < 0:
            return False
    if features.get("npr", 1) <= 0:
        return False
    return True
