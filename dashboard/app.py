"""Streamlit dashboard for inspecting prediction logs."""
from __future__ import annotations

import os
import json
from pathlib import Path
from datetime import date

import pandas as pd
import streamlit as st

LOG_FILE = Path("monitoring/predictions_log.csv")


def _authenticate() -> None:
    """Simple username/password gate using environment variables."""
    user = os.getenv("DASHBOARD_USER", "admin")
    password = os.getenv("DASHBOARD_PASS", "secret")

    if "auth" not in st.session_state:
        st.session_state.auth = False

    if st.session_state.auth:
        return

    st.sidebar.subheader("Login")
    u = st.sidebar.text_input("User")
    p = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login") and u == user and p == password:
        st.session_state.auth = True
    else:
        st.stop()


def _load_logs() -> pd.DataFrame:
    if not LOG_FILE.exists():
        return pd.DataFrame(columns=[
            "timestamp",
            "batch",
            "input",
            "prediction",
            "outcome",
            "improvement",
        ])
    df = pd.read_csv(LOG_FILE)
    if df.empty:
        return df
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["input"] = df["input"].apply(json.loads)
    return df


def main() -> None:
    _authenticate()
    st.title("Monitoring Dashboard")

    df = _load_logs()
    if df.empty:
        st.info("No logs available yet.")
        return

    batches = ["All"] + sorted(df["batch"].dropna().unique().tolist())
    batch = st.sidebar.selectbox("Batch", batches)
    start = st.sidebar.date_input("Start", df["timestamp"].min().date())
    end = st.sidebar.date_input("End", df["timestamp"].max().date())

    mask = (df["timestamp"].dt.date >= start) & (df["timestamp"].dt.date <= end)
    if batch != "All":
        mask &= df["batch"] == batch

    filtered = df[mask]

    st.subheader("Recent entries")
    st.dataframe(filtered.sort_values("timestamp", ascending=False).head(100))

    if filtered["outcome"].notna().any():
        st.subheader("Prediction vs Outcome")
        chart_df = filtered.set_index("timestamp")[
            ["prediction", "outcome"]
        ]
        st.line_chart(chart_df)
    else:
        st.info("No outcome data to plot.")

    if filtered["improvement"].notna().any():
        st.subheader("Uplift over time")
        uplift_df = filtered.set_index("timestamp")["improvement"]
        st.line_chart(uplift_df)
    else:
        st.info("No improvement data to plot.")


if __name__ == "__main__":  # pragma: no cover
    main()
