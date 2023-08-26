"""Get Graph data"""
from datetime import datetime
from typing import Any, List

from fastapi.responses import ORJSONResponse
from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud
from app.api import deps

router = APIRouter()


# GET
@router.get("/ppi/", response_model=ORJSONResponse)
def get_ppi_graph(
    db: Session = Depends(deps.get_db),
    ppi_id: int = Query(None, description="PPI ID", gt=0),
):
    """
    Get All PPI data
    """
    graph = crud.ppi_graph.get_all_ppi(db)
    if not graph:
        raise HTTPException(status_code=404, detail="PPIs not found")
    if ppi_id:
        graph = crud.ppi_graph.get_ppi_by_id(db, id=ppi_id)
        if not graph:
            raise HTTPException(status_code=404, detail="PPI not found")
    breakpoint()
    return graph


@router.get("/cluster/", response_model=ORJSONResponse)
def get_cluster_graph(
    db: Session = Depends(deps.get_db),
    cluster_id: int = Query(None, description="Cluster ID", gt=0),
):
    """
    Get All Cluster data
    """
    graph = crud.cluster_graph.get_all_cluster(db)
    if not graph:
        raise HTTPException(status_code=404, detail="Clusters not found")
    if cluster_id:
        graph = crud.cluster_graph.get_cluster_by_id(db, id=cluster_id)
        if not graph:
            raise HTTPException(status_code=404, detail="Cluster not found")
    breakpoint()
    return graph
