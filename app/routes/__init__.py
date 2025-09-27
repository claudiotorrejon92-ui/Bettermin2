from fastapi import APIRouter
from .active_learning import router as active_router
from .forecast import router as forecast_router
from .lab import router as lab_router
from .lotes import router as lotes_router
from .modelcard import router as modelcard_router
from .ml import router as ml_router
from .muestras import router as muestras_router
from .recommendations import router as recommendations_router
from .route import router as route_router

api_router = APIRouter()
api_router.include_router(lotes_router, prefix="/lotes", tags=["lotes"])

api_router.include_router(muestras_router, prefix="/muestras", tags=["muestras"])
api_router.include_router(ml_router, prefix="/ml", tags=["ml"])
api_router.include_router(lab_router, prefix="/lab", tags=["lab"])
api_router.include_router(forecast_router, prefix="/forecast", tags=["forecast"])
api_router.include_router(route_router, tags=["route"])
api_router.include_router(active_router, tags=["active_learning"])
api_router.include_router(modelcard_router, prefix="/modelcard", tags=["modelcard"])
api_router.include_router(
    recommendations_router, prefix="/recommendations", tags=["recommendations"]
)
