"""Protein API Router."""

from fastapi import APIRouter, Depends, HTTPException, Query  # noqa F401 # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from app import crud
from app.api import deps
from app.schemas import ProteinBase, ProteinResponse
import requests

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
    _response = [ProteinBase(**p.__dict__) for p in protein]  # type: ignore
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


@router.get("/interactions/{cluster_id}")
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
        return []
    _response = [ProteinBase(**p.__dict__) for p in _proteins]
    response = ProteinResponse(proteins=_response)
    return response


@router.get("/{protein_name}/uniprot/")
def get_data_from_uniprot(
    protein_name: str,
):
    """
    Get data from uniprot
    """
    _url = f"https://rest.uniprot.org/uniprotkb/{protein_name}/"

    # https://rest.uniprot.org/uniprotkb/YML046W
    _headers = {"Accept": "application/json"}
    response = requests.get(_url, headers=_headers)
    if response.status_code == 200:
        final_response = {
            "protein": protein_name,
            "data": "https://www.uniprot.org/uniprotkb/" + protein_name,
            "is_url": True,
        }
        return final_response
    return {
        "protein": protein_name,
        "data": "This protein id is not a valid Uniprot ID",
        "is_url": False,
    }
