"""
Feature store interfaces and implementations.

Provides an abstract interface for persisting tabular and time series data
along with concrete implementations for DuckDB, PostgreSQL and Google Sheets.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

import pandas as pd


class AbstractFeatureStore(ABC):
    """Abstract feature store interface."""

    @abstractmethod
    def save_table(self, df: pd.DataFrame, name: str) -> None:
        """Persist a DataFrame as a named table."""
        raise NotImplementedError

    @abstractmethod
    def save_timeseries(self, df: pd.DataFrame, name: str, timestamp_col: str) -> None:
        """Persist a time series DataFrame sorted by timestamp."""
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        """Close connections if necessary."""
        raise NotImplementedError


class DuckDBFeatureStore(AbstractFeatureStore):
    """Persist data to DuckDB and accompanying Parquet files."""

    def __init__(self, db_path: Path = Path("storage/feature_store.duckdb"),
                 parquet_dir: Path = Path("storage/parquet")) -> None:
        import duckdb  # local import to avoid hard dependency when unused

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
        ordered = df.sort_values(timestamp_col)
        self.save_table(ordered, name)

    def close(self) -> None:
        self.conn.close()


class PostgresFeatureStore(AbstractFeatureStore):
    """Persist data to a PostgreSQL database using SQLAlchemy."""

    def __init__(self, conn_str: str, schema: Optional[str] = None) -> None:
        from sqlalchemy import create_engine

        self.engine = create_engine(conn_str)
        self.schema = schema

    def save_table(self, df: pd.DataFrame, name: str) -> None:
        df.to_sql(name, self.engine, schema=self.schema, if_exists="append", index=False)

    def save_timeseries(self, df: pd.DataFrame, name: str, timestamp_col: str) -> None:
        ordered = df.sort_values(timestamp_col)
        self.save_table(ordered, name)

    def close(self) -> None:
        self.engine.dispose()


class SheetsFeatureStore(AbstractFeatureStore):
    """Persist data to a Google Sheets spreadsheet."""

    def __init__(self, creds_file: Path, spreadsheet: str) -> None:
        import gspread
        from google.oauth2.service_account import Credentials

        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file(str(creds_file), scopes=scopes)
        self.client = gspread.authorize(creds)
        self.spreadsheet = self.client.open(spreadsheet)

    def save_table(self, df: pd.DataFrame, name: str) -> None:
        worksheet = None
        try:
            worksheet = self.spreadsheet.worksheet(name)
            worksheet.clear()
        except Exception:
            worksheet = self.spreadsheet.add_worksheet(title=name, rows="100", cols="26")
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())

    def save_timeseries(self, df: pd.DataFrame, name: str, timestamp_col: str) -> None:
        ordered = df.sort_values(timestamp_col)
        self.save_table(ordered, name)

    def close(self) -> None:  # pragma: no cover - nothing to close
        pass


__all__ = [
    "AbstractFeatureStore",
    "DuckDBFeatureStore",
    "PostgresFeatureStore",
    "SheetsFeatureStore",
]
