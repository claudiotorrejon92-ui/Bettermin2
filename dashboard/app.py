"""Simple Streamlit dashboard for monitoring metrics."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

st.title("Monitoring Dashboard")

metrics_file = Path("monitoring/metrics.csv")
if metrics_file.exists():
    df = pd.read_csv(metrics_file)
    if not df.empty:
        st.line_chart(df.set_index(df.columns[0]))
    else:
        st.info("Metrics file is empty.")
else:
    st.info("No metrics available yet. Populate 'monitoring/metrics.csv' to see plots.")
