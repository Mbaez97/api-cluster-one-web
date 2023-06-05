from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    # asgard,
    cluster_one,
    protein,
)

api_router = APIRouter()
api_router.include_router(cluster_one.router, prefix="/cluste_one", tags=["cluste_one"])
api_router.include_router(protein.router, prefix="/protein", tags=["protein"])
# api_router.include_router(asgard.router, prefix="/asgard", tags=["asgard"])
