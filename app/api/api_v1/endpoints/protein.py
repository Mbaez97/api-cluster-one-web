"""Assigns Raspadita box, libro and cartones"""
from datetime import datetime
from typing import Any, List

from fastapi.responses import ORJSONResponse
from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.schemas import ProteinBase, ProteinResponse

router = APIRouter()


# GET
@router.get("/", response_model=ProteinResponse)
def get_protein(
    db: Session = Depends(deps.get_db),
    protein_id: int = Query(None, description="Protein ID", gt=0),
):
    """
    Get All Protein data
    """
    protein = crud.protein.get_all(db)
    if not protein:
        raise HTTPException(status_code=404, detail="Proteins not found")
    if protein_id:
        protein = crud.protein.get_by_id(db, id=protein_id)
        if not protein:
            raise HTTPException(status_code=404, detail="Protein not found")
    _response = [ProteinBase(**p.__dict__) for p in protein]
    response = ProteinResponse(proteins=_response)
    return response


@router.get("/{protein_name}/data", response_model=ProteinBase)
def get_protein_data(
    protein_name: str,
    db: Session = Depends(deps.get_db),
):
    """
    Get protein data
    """
    protein = crud.protein.get_by_name(db, name=protein_name)
    if not protein:
        raise HTTPException(status_code=404, detail="Protein not found")
    response = ProteinBase(**protein.__dict__)
    return response


@router.get("/interactions/{cluster_id}", response_model=ProteinResponse)
def get_proteins_interactions(
    cluster_id: int,
    db: Session = Depends(deps.get_db),
):
    """
    Get protein interactions
    """
    _cluster_graph = crud.cluster_graph.get_cluster_by_id(db, id=cluster_id)
    if not _cluster_graph:
        raise HTTPException(status_code=404, detail="Cluster not found")
    _proteins = crud.protein.get_all_by_cluster(db, cluster_id=cluster_id)
    if not _proteins:
        raise HTTPException(status_code=404, detail="Protein not found")
    _response = [ProteinBase(**p.__dict__) for p in _proteins]
    response = ProteinResponse(proteins=_response)
    return response
