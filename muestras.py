"""
Endpoints for operations on ``Muestra`` resources.

This module exposes CRUD endpoints to create and retrieve muestras.  When
creating a muestra you can embed an optional ``geoquimica`` object, which
will be persisted alongside the muestra.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, db


router = APIRouter()


@router.post("/", response_model=schemas.Muestra)
def create_muestra(muestra: schemas.MuestraCreate, db_session: Session = Depends(db.get_db)):
    """Crear una nueva muestra asociada a un lote existente."""
    existing = db_session.query(models.Muestra).filter(models.Muestra.muestra_id == muestra.muestra_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Muestra already exists")
    # Ensure the lote exists
    lote = db_session.query(models.Lote).filter(models.Lote.lote_id == muestra.lote_id).first()
    if not lote:
        raise HTTPException(status_code=400, detail="Associated lote not found")

    db_muestra = models.Muestra(
        muestra_id=muestra.muestra_id,
        lote_id=muestra.lote_id,
        codigo_campo=muestra.codigo_campo,
        tipo_muestra=muestra.tipo_muestra,
        metodo_muestreo=muestra.metodo_muestreo,
        fecha_muestreo=muestra.fecha_muestreo,
        masa_muestra_kg=muestra.masa_muestra_kg,
        humedad_pct=muestra.humedad_pct,
    )
    # If geoquimica is provided embed it
    if muestra.geoquimica:
        db_geo = models.Geoquimica(**muestra.geoquimica.dict())
        db_muestra.geoquimica = db_geo

    db_session.add(db_muestra)
    db_session.commit()
    db_session.refresh(db_muestra)
    return db_muestra


@router.get("/", response_model=List[schemas.Muestra])
def read_muestras(skip: int = 0, limit: int = 100, db_session: Session = Depends(db.get_db)):
    """Listar todas las muestras con paginación opcional."""
    return db_session.query(models.Muestra).offset(skip).limit(limit).all()


@router.get("/{muestra_id}", response_model=schemas.Muestra)
def read_muestra(muestra_id: str, db_session: Session = Depends(db.get_db)):
    """Obtener una muestra por su identificador."""
    muestra = db_session.query(models.Muestra).filter(models.Muestra.muestra_id == muestra_id).first()
    if not muestra:
        raise HTTPException(status_code=404, detail="Muestra not found")
    return muestra