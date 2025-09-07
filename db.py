"""
Database configuration and session management for Eco‑Pilot Caracterización.

This module defines a SQLAlchemy engine and session factory.  By default it
uses a local SQLite database (``app.db``) stored in the repository root.  To
migrate to another database (e.g. PostgreSQL or MySQL) change the
``DATABASE_URL`` constant accordingly.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


DATABASE_URL = "sqlite:///./app.db"

# The connect_args flag is needed only for SQLite.  For other databases it
# can be omitted.
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a configured "Session" class and a Session instance bound to the engine.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative class definitions.
Base = declarative_base()


def get_db():
    """
    Dependency that provides a database session to path operations.

    Yields a SQLAlchemy session and ensures it is closed after the request
    finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()