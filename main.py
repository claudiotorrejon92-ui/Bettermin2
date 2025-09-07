"""
Application entry point for Eco‑Pilot Caracterización API.

This module creates the FastAPI application, generates database tables on
startup and includes the routers defined in ``app/routes``.  When executed
with Uvicorn it exposes a RESTful API for managing lotes, muestras y
geoquímica.
"""

from fastapi import FastAPI

from .db import Base, engine
from .routes import api_router


def create_application() -> FastAPI:
    """Instantiate the FastAPI application and configure routes."""
    # Create database tables if they don't exist
    Base.metadata.create_all(bind=engine)

    app = FastAPI(
        title="Eco‑Pilot Caracterización API",
        description="API para gestionar datos de caracterización de relaves",
        version="0.1.0",
    )
    app.include_router(api_router)
    return app


app = create_application()