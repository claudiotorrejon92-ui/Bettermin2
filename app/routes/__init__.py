from fastapi import APIRouter
from .lotes import router as lotes_router
from .muestras import router as muestras_router
from .ml import router as ml_router
from .lab import router as lab_router

api_router = APIRouter()
api_router.include_router(lotes_router, prefix="/lotes", tags=["lotes"])

api_router.include_router(muestras_router, prefix="/muestras", tags=["muestras"])
api_router.include_router(ml_router, prefix="/ml", tags=["ml"])
api_router.include_router(lab_router, prefix="/lab", tags=["lab"])
