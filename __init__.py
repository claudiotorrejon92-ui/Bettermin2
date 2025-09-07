"""
Package initialization for the FastAPI backend of Eco‑Pilot Caracterización.

This package exposes the API application via `app.main` and consolidates
database utilities, ORM models, Pydantic schemas and route definitions.
"""

__all__ = [
    "db",
    "models",
    "schemas",
    "main",
]