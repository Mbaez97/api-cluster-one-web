from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    cluster_one,
    protein,
    graph,
)

api_router = APIRouter()
api_router.include_router(
    cluster_one.router, prefix="/cluster_one", tags=["cluster_one"]
)
api_router.include_router(protein.router, prefix="/protein", tags=["protein"])
api_router.include_router(graph.router, prefix="/graph", tags=["graph"])
