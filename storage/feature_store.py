"""
DuckDB/Parquet backed feature store.

This module provides a small utility class to persist both tabular data and
ordered time series to a local DuckDB database and accompanying Parquet files.
"""

from pathlib import Path
from typing import Optional

import duckdb
import pandas as pd


class FeatureStore:
    """Persist tabular and time series data to DuckDB and Parquet."""

    def __init__(self, db_path: Path = Path("storage/feature_store.duckdb"),
                 parquet_dir: Path = Path("storage/parquet")) -> None:
        self.db_path = db_path
        self.parquet_dir = parquet_dir
        self.parquet_dir.mkdir(parents=True, exist_ok=True)
        self.conn = duckdb.connect(str(self.db_path))

    def save_table(self, df: pd.DataFrame, name: str) -> None:
        """Save a DataFrame as a table and Parquet file."""
        self.conn.register("df_view", df)
        self.conn.execute(
            f"CREATE TABLE IF NOT EXISTS {name} AS SELECT * FROM df_view WHERE 1=0"
        )
        self.conn.execute(f"INSERT INTO {name} SELECT * FROM df_view")
        parquet_path = self.parquet_dir / f"{name}.parquet"
        df.to_parquet(parquet_path, index=False)

    def save_timeseries(self, df: pd.DataFrame, name: str, timestamp_col: str) -> None:
        """Persist a time series DataFrame sorted by timestamp."""
        ordered = df.sort_values(timestamp_col)
        self.save_table(ordered, name)

    def close(self) -> None:
        """Close the underlying DuckDB connection."""
        self.conn.close()
