"""Assigns Raspadita box, libro and cartones"""
import os
from time import sleep
from datetime import datetime
from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.orm import Session

# from app import crud
from app.api import deps
from app import crud
from app.api.utils import execute_cluster_one

router = APIRouter()

# ClusterOne API
@router.post("/clusterone/quickrun")
def get_quickrun(
    db: Session = Depends(deps.get_db),
    pp_id: int = Query(None, description="PPI ID", gt=0),
):
    """
    Get All Cluster data
    """
    _base_command ="java -jar cluster_one-1.0.jar"
    _final_command = "> complex_cluster_response.txt"
    if pp_id:
        ppi_obj = crud.ppi_graph.get_ppi_by_id(db, id=pp_id)
        if not ppi_obj:
            raise HTTPException(status_code=404, detail="PPI not found")
        _command = f"{_base_command} {ppi_obj.data} {_final_command}"
    else:
        # TODO: User send txt in body and save it in a file
        # And then run the command With the file
        _command = f"{_base_command} {_final_command}"
    response = execute_cluster_one(_command)
    # os.system(_command)
    # sleep(2)
    # with open("complex_cluster_response.txt", "r") as f:
    #     response = f.read()
    # os.system("rm complex_cluster_response.txt")
    _clusters = []
    for complex in response:
        _proteins_obj = []
        _edges = []
        _proteins = complex.split("\t")
        for protein in _proteins:
            _protein_obj = crud.protein.get_by_name(db, name=protein)
            if not _protein_obj:
                # Create Protein in db
                _protein_obj = crud.protein.quick_creation(db, name=protein)
            _proteins_obj.append(_protein_obj)
        for _protein in _proteins_obj:
            for _protein2 in _proteins_obj:
                if _protein.id != _protein2.id:
                    _edge = {
                        "data": {
                            "source": _protein.id,
                            "target": _protein2.id,
                            "weight": 1,
                            "interaction": "pp",
                            "id": str(_protein.id) + "_" + str(_protein2.id)
                        },
                        "position": {},
                        "selected": False,
                        "selectable": True,
                        "locked": False,
                        "grabbable": True,
                        "group": "edges",
                        "classes": "pp"
                    }
                    _edges.append(_edge)
        _clusters.append({
            "nodes": _proteins_obj,
            "edges": _edges
        })
    return _clusters
