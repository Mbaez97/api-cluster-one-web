"""Assigns Raspadita box, libro and cartones"""
import os
from time import sleep
from datetime import datetime
from typing import Any, List
import random

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.orm import Session

# from app import crud
from app.api import deps
from app import crud
from app.api.utils import execute_cluster_one

router = APIRouter()

# ClusterOne API
@router.post("/quickrun/")
def get_quickrun(
    db: Session = Depends(deps.get_db),
    pp_id: int = Query(None, description="PPI ID", gt=0),
    cant_clusters: int = Query(None, description="Number of clusters", gt=0),
    # cluster_one_version: str = Query(None, description="ClusterOne Version", gt=0),
):
    """
    Get All Cluster data
    TODO: 
        - Add a file upload
    """
    _base_command = "java -jar cluster_one-1.0.jar"

    # if not cluster_one_version:
    #     _base_command = "java -jar cluster_one-1.0.jar"
    # else:
        # _base_command = f"java -jar cluster_one-{cluster_one_version}.jar"
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
    _clusters = {}
    if cant_clusters:
        response = response[:cant_clusters]
    for complex in response:
        _proteins_obj = []
        _edges = []
        _proteins = complex.split("\t")
        for protein in _proteins:
            _protein_obj = crud.protein.get_by_name(db, name=protein)
            if not _protein_obj:
                # Create Protein in db
                _protein_obj = crud.protein.quick_creation(db, name=protein)
            _protein_node = {
                "data": {
                    "id": _protein_obj.id,
                    "name": _protein_obj.name,
                    "protein": "true"
                },
                "position": {
                    "x": random.randint(800, 1000),
                    "y": random.randint(0, 100)
                },
                "selected": False,
                "selectable": True,
                "locked": False,
                "grabbable": True,
                "group": "nodes",
                "style": _protein_obj.style.ccs_styles,
            }
            _proteins_obj.append(_protein_node)
        for _protein in _proteins_obj:
            for _protein2 in _proteins_obj:
                if _protein["data"]["id"] != _protein2["data"]["id"]:
                    _edge = {
                        "data": {
                            "source": _protein["data"]["id"],
                            "target": _protein2["data"]["id"],
                            "weight": 1,
                            "interaction": "pp",
                            "id": str(_protein["data"]["id"]) + "_" + str(_protein2["data"]["id"])
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
        _clusters.update({
            "nodes": _proteins_obj,
            "edges": _edges
        })
    return _clusters

@router.post("/run/")
def get_run(
    db: Session = Depends(deps.get_db),
    pp_id: int = Query(None, description="PPI ID", gt=0),
    cant_clusters: int = Query(None, description="Number of clusters", gt=0),
    body: Any = Body(...),
    # cluster_one_version: str = Query(None, description="ClusterOne Version", gt=0),
):
    """
    Get All Cluster data
    TODO: 
        - Add a file upload
    """
    _base_command = "java -jar cluster_one-1.0.jar"

    # if not cluster_one_version:
    #     _base_command = "java -jar cluster_one-1.0.jar"
    # else:
        # _base_command = f"java -jar cluster_one-{cluster_one_version}.jar"
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
    response = execute_cluster_one(_command, body)
    _clusters = {}
    if cant_clusters:
        response = response[:cant_clusters]
    for complex in response:
        _proteins_obj = []
        _edges = []
        _proteins = complex.split("\t")
        for protein in _proteins:
            _protein_obj = crud.protein.get_by_name(db, name=protein)
            if not _protein_obj:
                # Create Protein in db
                _protein_obj = crud.protein.quick_creation(db, name=protein)
            _protein_node = {
                "data": {
                    "id": _protein_obj.id,
                    "name": _protein_obj.name,
                    "protein": "true"
                },
                "position": {
                    "x": random.randint(800, 1000),
                    "y": random.randint(0, 100)
                },
                "selected": False,
                "selectable": True,
                "locked": False,
                "grabbable": True,
                "group": "nodes",
                "style": _protein_obj.style.ccs_styles,
            }
            _proteins_obj.append(_protein_node)
        for _protein in _proteins_obj:
            for _protein2 in _proteins_obj:
                if _protein["data"]["id"] != _protein2["data"]["id"]:
                    _edge = {
                        "data": {
                            "source": _protein["data"]["id"],
                            "target": _protein2["data"]["id"],
                            "weight": 1,
                            "interaction": "pp",
                            "id": str(_protein["data"]["id"]) + "_" + str(_protein2["data"]["id"])
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
        _clusters.update({
            "nodes": _proteins_obj,
            "edges": _edges
        })
    return _clusters