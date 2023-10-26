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
    size: int = Query(100, description="Size of the response", gt=0),
    offset: int = Query(0, description="Offset of the response", ge=0),
):
    """
    Get data from uniprot
    """
    _url_base = "https://www.ebi.ac.uk/proteins/api/proteins"
    params = f"offset={offset}&size={size}&protein={protein_name}"
    _url = f"{_url_base}?{params}"
    _headers = {"Accept": "application/json"}
    response = requests.get(_url, headers=_headers)
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Protein not found")
    data = response.json()
    _final_response = []
    for d in data:
        _complete_str = ""
        _complete_name = ""
        _has_recommend_name = False
        _has_submitted_name = False
        _has_other_name = False

        _protein = d["protein"]
        _genes = d["gene"]
        _organism = d["organism"]

        _has_recommend_name = True if "recommendedName" in _protein else False
        _has_submitted_name = True if "submittedName" in _protein else False
        _has_other_name = True if "alternativeNames" in _protein else False

        if _has_recommend_name:
            _recommend_name = _protein["recommendedName"]
            _recommend_name_full = _recommend_name["fullName"]["value"]
            _complete_name += f"Recommended name: {_recommend_name_full}"
        if _has_submitted_name:
            for _submitted_name in _protein["submittedName"]:
                _submitted_name_full = _submitted_name["fullName"]["value"]
                _evidences = _submitted_name["fullName"]["evidences"]
                _evidences_str = "\nEvidences: "
                for _evidence in _evidences:
                    try:
                        _evidence_code = _evidence["code"]
                        _evidence_code_str = _evidence_code["source"]["name"]
                        _evidences_str += _evidence_code_str
                    except Exception:
                        pass
                _complete_name += f"Submitted name: {_submitted_name_full}"
                _complete_name += _evidences_str
        if _has_other_name:
            for _other_name in _protein["alternativeNames"]:
                _other_name_full = _other_name["fullName"]
                _complete_name += f"\nOther name: {_other_name_full}"

        _complete_str += _complete_name + " \n"
        _complete_str += "\nOrganism: \n"
        for _orga_name in _organism["names"]:
            _type_orga_name = _orga_name["type"].upper()
            _orga_name_full = _orga_name["value"]
            _complete_str += (
                f"\nType: {_type_orga_name} Name: {_orga_name_full} \n"  # noqa E501
            )
        _linages = _organism["lineage"]
        _linage_str = "\nLineage: "
        for _linage in _linages:
            _linage_prev_str = f"\n * {_linage}"
            _linage_str += _linage_prev_str
        _complete_str += _linage_str

        _complete_str += "\nGene: \n"
        for _gene in _genes:
            try:
                _gene_names = _gene["orfNames"]
                _gene_names_str = "\nORF names: "
                for _gene_name in _gene_names:
                    _gene_names_str += _gene_name["value"]
                    _evidences_name = _gene_name["evidences"]
                    _evidences_name_str = "\nEvidences: "
                    for _evidence_name in _evidences_name:
                        try:
                            _evidence_code = _evidence_name["code"]
                            _evidence_code_str = _evidence_code["source"][
                                "name"
                            ]  # noqa E501
                            _evidences_name_str += _evidence_code_str
                        except Exception as e:
                            print(e)
                    _gene_names_str += _evidences_name_str
                _complete_str += _gene_names_str
            except Exception:
                pass
        _final_response.append(_complete_str)

    real_final_response = {
        "protein": protein_name,
        "data": _final_response,
    }
    return real_final_response
