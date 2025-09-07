"""
Endpoints for operations on ``Lote`` resources.

Provides CRUD endpoints to create, list and retrieve lotes.  New lotes are
validated against the Pydantic schema before being persisted.  Duplicate
identifiers are rejected with an HTTP 400 error.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, db


router = APIRouter()


@router.post("/", response_model=schemas.Lote)
def create_lote(lote: schemas.LoteCreate, db_session: Session = Depends(db.get_db)):
    """Crear un nuevo lote.  El ``lote_id`` debe ser único."""
    existing = db_session.query(models.Lote).filter(models.Lote.lote_id == lote.lote_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Lote already exists")
    db_lote = models.Lote(**lote.dict())
    db_session.add(db_lote)
    db_session.commit()
    db_session.refresh(db_lote)
    return db_lote


@router.get("/", response_model=List[schemas.Lote])
def read_lotes(skip: int = 0, limit: int = 100, db_session: Session = Depends(db.get_db)):
    """Listar lotes existentes con paginación opcional."""
    return db_session.query(models.Lote).offset(skip).limit(limit).all()


@router.get("/{lote_id}", response_model=schemas.Lote)
def read_lote(lote_id: str, db_session: Session = Depends(db.get_db)):
    """Obtener un lote por su identificador."""
    lote = db_session.query(models.Lote).filter(models.Lote.lote_id == lote_id).first()
    if not lote:
        raise HTTPException(status_code=404, detail="Lote not found")
    return lote
