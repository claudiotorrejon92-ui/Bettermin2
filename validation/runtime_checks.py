"""Runtime constraint validation utilities."""
from __future__ import annotations

from typing import Callable, Dict

import pandas as pd


class ConstraintViolation(Exception):
    """Raised when a runtime constraint is violated."""


def validate_runtime(
    df: pd.DataFrame, constraints: Dict[str, Callable[[pd.Series], pd.Series]]
) -> None:
    """Validate a dataframe against column-wise constraints.

    Parameters
    ----------
    df:
        DataFrame to validate.
    constraints:
        Mapping of column name to a callable returning a boolean Series of valid
        entries.

    Raises
    ------
    ConstraintViolation
        If any constraint is not satisfied.
    """
    for column, rule in constraints.items():
        if column not in df.columns:
            raise ConstraintViolation(f"Missing required column: {column}")
        mask = rule(df[column])
        if not mask.all():
            invalid = df.index[~mask].tolist()
            raise ConstraintViolation(
                f"Constraint failed for column '{column}' at rows {invalid}"
            )
