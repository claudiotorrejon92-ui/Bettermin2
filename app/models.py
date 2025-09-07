"""
SQLAlchemy models for Eco‑Pilot Caracterización.

These ORM classes represent the core entities of the tailings characterization
module: ``Lote`` (lots or spatial units), ``Muestra`` (individual samples)
and ``Geoquimica`` (laboratory geochemical results).  The relationships
between them reflect a one‑to‑many hierarchy where a lote can have many
muestras and a muestra can have at most one set of geoquímicos.
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from .db import Base


class Lote(Base):
    """Representa un lote o unidad espacial dentro del depósito de relaves."""

    __tablename__ = "lotes"

    lote_id = Column(String, primary_key=True, index=True)
    deposito_id = Column(String, nullable=True)
    nombre_lote = Column(String, nullable=True)
    ubicacion_wgs84_lat = Column(Float, nullable=True)
    ubicacion_wgs84_lon = Column(Float, nullable=True)
    estado_lote = Column(String, nullable=True)
    volumen_m3_estimado = Column(Float, nullable=True)
    densidad_t_m3_estimada = Column(Float, nullable=True)
    toneladas_estimadas = Column(Float, nullable=True)

    # Relationship to muestras
    muestras = relationship("Muestra", back_populates="lote", cascade="all, delete-orphan")


class Muestra(Base):
    """Representa una muestra individual tomada de un lote."""

    __tablename__ = "muestras"

    muestra_id = Column(String, primary_key=True, index=True)
    lote_id = Column(String, ForeignKey("lotes.lote_id"))
    codigo_campo = Column(String, nullable=True)
    tipo_muestra = Column(String, nullable=True)
    metodo_muestreo = Column(String, nullable=True)
    fecha_muestreo = Column(String, nullable=True)
    masa_muestra_kg = Column(Float, nullable=True)
    humedad_pct = Column(Float, nullable=True)

    # Relationship back to lote and forward to geoquimica
    lote = relationship("Lote", back_populates="muestras")
    geoquimica = relationship("Geoquimica", back_populates="muestra", uselist=False, cascade="all, delete-orphan")


class Geoquimica(Base):
    """Resultados de laboratorio (geoquímica) para una muestra."""

    __tablename__ = "geoquimica"

    id = Column(Integer, primary_key=True, index=True)
    muestra_id = Column(String, ForeignKey("muestras.muestra_id"))
    laboratorio = Column(String, nullable=True)
    metodo_analitico = Column(String, nullable=True)
    Au_g_t = Column(Float, nullable=True)
    Ag_g_t = Column(Float, nullable=True)
    Cu_pct = Column(Float, nullable=True)
    Fe_pct = Column(Float, nullable=True)
    S_total_pct = Column(Float, nullable=True)
    S_sulfuro_pct = Column(Float, nullable=True)
    As_ppm = Column(Float, nullable=True)
    Sb_ppm = Column(Float, nullable=True)

    # Relationship back to muestra
    muestra = relationship("Muestra", back_populates="geoquimica")
