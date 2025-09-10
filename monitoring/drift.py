"""Drift detection utilities using Evidently with Prometheus integration."""
from __future__ import annotations

from typing import Iterable, Dict

import pandas as pd
from evidently.metrics import ColumnDriftMetric
from evidently.report import Report
from prometheus_client import Gauge


KS_GAUGE = Gauge(
    "feature_ks_stat", "Kolmogorov-Smirnov statistic for feature drift", ["feature"]
)
PSI_GAUGE = Gauge(
    "feature_psi", "Population Stability Index for feature drift", ["feature"]
)


def log_drift(
    reference: pd.DataFrame, current: pd.DataFrame, columns: Iterable[str]
) -> Dict[str, Dict[str, float]]:
    """Compute KS and PSI drift metrics and export them via Prometheus.

    Parameters
    ----------
    reference, current:
        Historical (reference) data and current batch to compare.
    columns:
        Iterable of column names to evaluate.

    Returns
    -------
    dict
        Mapping of column name to computed KS and PSI values.
    """
    results: Dict[str, Dict[str, float]] = {}
    for column in columns:
        report = Report(
            metrics=[
                ColumnDriftMetric(column_name=column, stattest="ks"),
                ColumnDriftMetric(column_name=column, stattest="psi"),
            ]
        )
        report.run(reference_data=reference, current_data=current)
        metrics = report.as_dict()["metrics"]
        ks_value = metrics[0]["result"]["drift_score"]
        psi_value = metrics[1]["result"]["drift_score"]
        KS_GAUGE.labels(column).set(ks_value)
        PSI_GAUGE.labels(column).set(psi_value)
        results[column] = {"ks": ks_value, "psi": psi_value}
    return results
