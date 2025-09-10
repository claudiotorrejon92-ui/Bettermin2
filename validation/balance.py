"""
Mass/atom balance utilities and physico‑chemical validation rules.

These helpers are meant to be used during data validation stages to guarantee
that compositions and measurements obey conservation laws and basic
physical chemistry constraints.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Dict

import pandas as pd


FORMULA_RE = re.compile(r"([A-Z][a-z]?)(\d*)")


def parse_formula(formula: str) -> Counter:
    """Parse a chemical formula into element counts."""
    counts: Counter[str] = Counter()
    for element, qty in FORMULA_RE.findall(formula):
        counts[element] += int(qty) if qty else 1
    return counts


def atom_balance(reactants: Dict[str, int], products: Dict[str, int]) -> bool:
    """Check atomic balance between reactants and products.

    Parameters
    ----------
    reactants, products:
        Mapping of chemical formula to stoichiometric coefficient.
    """
    r_counter: Counter[str] = Counter()
    p_counter: Counter[str] = Counter()
    for formula, coeff in reactants.items():
        r_counter += parse_formula(formula) * coeff
    for formula, coeff in products.items():
        p_counter += parse_formula(formula) * coeff
    return r_counter == p_counter


def check_mass_fractions(composition: Dict[str, float], tol: float = 1e-3) -> bool:
    """Validate that mass fractions sum to one within tolerance."""
    total = sum(composition.values())
    return abs(total - 1.0) <= tol


def enforce_physicochemical_rules(df: pd.DataFrame) -> pd.DataFrame:
    """Apply simple physico‑chemical sanity checks.

    Negative concentrations are clipped to zero and pH values are forced to the
    [0, 14] interval.
    """
    num_cols = df.select_dtypes("number").columns
    df[num_cols] = df[num_cols].clip(lower=0)
    if "pH" in df.columns:
        df.loc[:, "pH"] = df["pH"].clip(lower=0, upper=14)
    return df
