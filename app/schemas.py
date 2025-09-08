"""
Pydantic schemas for Eco‑Pilot Caracterización.

These classes define the data shapes used for request and response bodies.  The
``orm_mode = True`` configuration tells Pydantic to read data from ORM
instances (SQLAlchemy models) and convert them to plain dicts.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class GeoquimicaBase(BaseModel):
    laboratorio: Optional[str] = None
    metodo_analitico: Optional[str] = None
    Au_g_t: Optional[float] = None
    Ag_g_t: Optional[float] = None
    Cu_pct: Optional[float] = None
    Fe_pct: Optional[float] = None
    S_total_pct: Optional[float] = None
    S_sulfuro_pct: Optional[float] = None
    As_ppm: Optional[float] = None
    Sb_ppm: Optional[float] = None


class GeoquimicaCreate(GeoquimicaBase):
    pass


class Geoquimica(GeoquimicaBase):
    id: int
    muestra_id: str

    class Config:
        orm_mode = True


class MuestraBase(BaseModel):
    muestra_id: str
    lote_id: str
    codigo_campo: Optional[str] = None
    tipo_muestra: Optional[str] = None
    metodo_muestreo: Optional[str] = None
    fecha_muestreo: Optional[str] = None
    masa_muestra_kg: Optional[float] = None
    humedad_pct: Optional[float] = None


class MuestraCreate(MuestraBase):
    geoquimica: Optional[GeoquimicaCreate] = None


class Muestra(MuestraBase):
    geoquimica: Optional[Geoquimica] = None

    class Config:
        orm_mode = True


class LoteBase(BaseModel):
    lote_id: str
    deposito_id: Optional[str] = None
    nombre_lote: Optional[str] = None
    ubicacion_wgs84_lat: Optional[float] = None
    ubicacion_wgs84_lon: Optional[float] = None
    estado_lote: Optional[str] = None
    volumen_m3_estimado: Optional[float] = None
    densidad_t_m3_estimada: Optional[float] = None
    toneladas_estimadas: Optional[float] = None


class LoteCreate(LoteBase):
    pass


class Lote(LoteBase):
    muestras: List[Muestra] = Field(default_factory=list)

    class Config:
        orm_mode = True
