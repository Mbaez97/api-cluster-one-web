"""Assigns Raspadita box, libro and cartones"""
import os
from time import sleep
from datetime import datetime
from typing import Any, List
import random
import json

from fastapi import APIRouter, Body, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

# from app import crud
from app.api import deps
from app import crud
from app.api.utils import execute_cluster_one
from uuid import uuid4
from app.models import Layout


router = APIRouter()


def get_default_uuid():
    return str(uuid4())


def get_random_layout():
    return random.choice(
        [
            "force",
            "cose",
            "circle",
            "concentric",
            "grid",
            "breadthfirst",
            "cose-bilkent",
            "cola",
            "euler",
            "spread",
            "dagre",
            "klay",
            "random",
        ]
    )


# ClusterOne API
@router.post("/quickrun/")
def get_quickrun(
    db: Session = Depends(deps.get_db),
    pp_id: int = Query(None, description="PPI ID", gt=0),
    cant_clusters: int = Query(None, description="Number of clusters", gt=0),
    file: UploadFile = File(None),
    # cluster_one_version: str = Query(None, description="ClusterOne Version", gt=0),
):
    """
    Get All Cluster data
    TODO:
        - identify complex and create it in db, associate it with clusters
    """
    # if not cluster_one_version:
    #     _base_command = "java -jar cluster_one-1.0.jar"
    # else:
    # _base_command = f"java -jar cluster_one-{cluster_one_version}.jar"
    _base_command = "java -jar cluster_one-1.0.jar"
    _file_name = f"complex_cluster_response_{get_default_uuid()}.csv"
    _final_command = "> " + _file_name
    if file:
        # Save file in media
        with open(f"{file.filename}", "wb") as buffer:
            buffer.write(file.file.read())
            buffer.close()
        _command = f"{_base_command} {file.filename} -F csv {_final_command}"
        pp_id = None
    if pp_id:
        ppi_obj = crud.ppi_graph.get_ppi_by_id(db, id=pp_id)
        if not ppi_obj:
            raise HTTPException(status_code=404, detail="PPI not found")
        _command = f"{_base_command} {ppi_obj.data} -F csv {_final_command}"

    response = execute_cluster_one(_command, file_name=_file_name)
    _clusters = []
    if cant_clusters:
        response = response[:cant_clusters]
    for complex in response:
        _layout = db.query(Layout).filter(Layout.name == "random").first()
        _obj = {
            "external_weight": complex[4],
            "internal_weight": complex[3],
            "density": complex[2],
            "size": complex[1],
            "quality": complex[5],
            "layout": _layout,
            "data": "/app/app/media/clusters/" + _file_name,
        }
        _cluster_obj = crud.cluster_graph.create_cluster(db, obj=_obj)
        _proteins_obj = []
        _edges = []
        _proteins = complex[7].split(" ")
        for protein in _proteins:
            _protein_obj = crud.protein.get_by_name(db, name=protein)
            if not _protein_obj:
                # Create Protein in db
                _protein_obj = crud.protein.quick_creation(db, name=protein)
            _protein_node = {
                "data": {
                    "id": _protein_obj.id,
                    "name": _protein_obj.name,
                    "protein": "true",
                },
                "position": {
                    "x": random.randint(800, 1000),
                    "y": random.randint(0, 100),
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
                            "id": str(_protein["data"]["id"])
                            + "_"
                            + str(_protein2["data"]["id"]),
                        },
                        "position": {},
                        "selected": False,
                        "selectable": True,
                        "locked": False,
                        "grabbable": True,
                        "group": "edges",
                        "classes": "pp",
                    }
                    _edges.append(_edge)
        _clusters.append(
            {"cluster_id": _cluster_obj.id, "nodes": _proteins_obj, "edges": _edges}
        )
    if file:
        # Delete file
        os.system(f"rm {file.filename}")
    return _clusters


@router.post("/run/")
def get_run(
    db: Session = Depends(deps.get_db),
    pp_id: int = Query(None, description="PPI ID", gt=0),
    cant_clusters: int = Query(None, description="Number of clusters", gt=0),
    body: Any = Body(...),
    file: UploadFile = File(None),
    # cluster_one_version: str = Query(None, description="ClusterOne Version", gt=0),
):
    """
    Get All Cluster data
    TODO:
        - Add a file upload
    """

    # if not cluster_one_version:
    #     _base_command = "java -jar cluster_one-1.0.jar"
    # else:
    # _base_command = f"java -jar cluster_one-{cluster_one_version}.jar"
    _base_command = "java -jar cluster_one-1.0.jar"
    _file_name = f"complex_cluster_response_{get_default_uuid()}.csv"
    _final_command = "> " + _file_name
    if file:
        # Save file in media
        with open(f"{file.filename}", "wb") as buffer:
            buffer.write(file.file.read())
            buffer.close()
        _command = f"{_base_command} {file.filename} -F csv {_final_command}"
        pp_id = None
    if pp_id:
        ppi_obj = crud.ppi_graph.get_ppi_by_id(db, id=pp_id)
        if not ppi_obj:
            raise HTTPException(status_code=404, detail="PPI not found")
        _command = f"{_base_command} {ppi_obj.data} -F csv {_final_command}"
    if type(body) == str:
        body = json.loads(body)
    breakpoint()
    response = execute_cluster_one(_command, file_name=_file_name, params=body)
    _clusters = []
    if cant_clusters:
        response = response[:cant_clusters]
    for complex in response:
        _layout = db.query(Layout).filter(Layout.name == "random").first()
        _obj = {
            "external_weight": complex[4],
            "internal_weight": complex[3],
            "density": complex[2],
            "size": complex[1],
            "quality": complex[5],
            "layout": _layout,
            "data": "/app/app/media/clusters/" + _file_name,
        }
        _cluster_obj = crud.cluster_graph.create_cluster(db, obj=_obj)
        _proteins_obj = []
        _edges = []
        _proteins = complex[7].split(" ")
        for protein in _proteins:
            _protein_obj = crud.protein.get_by_name(db, name=protein)
            if not _protein_obj:
                # Create Protein in db
                _protein_obj = crud.protein.quick_creation(db, name=protein)
            _protein_node = {
                "data": {
                    "id": _protein_obj.id,
                    "name": _protein_obj.name,
                    "protein": "true",
                },
                "position": {
                    "x": random.randint(800, 1000),
                    "y": random.randint(0, 100),
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
                            "id": str(_protein["data"]["id"])
                            + "_"
                            + str(_protein2["data"]["id"]),
                        },
                        "position": {},
                        "selected": False,
                        "selectable": True,
                        "locked": False,
                        "grabbable": True,
                        "group": "edges",
                        "classes": "pp",
                    }
                    _edges.append(_edge)
        _clusters.append(
            {"cluster_id": _cluster_obj.id, "nodes": _proteins_obj, "edges": _edges}
        )
    if file:
        # Delete file
        os.system(f"rm {file.filename}")
    return _clusters


@router.get("/{cluster_id}/csv")
def get_csv(
    db: Session = Depends(deps.get_db),
    cluster_id: int = 0,
):
    """
    Get Csv Cluster data

    """
    cluster = crud.cluster_graph.get_cluster_by_id(db, id=cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    _csv_path = cluster.data
    _csv_name = _csv_path.split("/")[-1]
    # open file
    buffer = open(_csv_path, "r")
    # return csv
    return StreamingResponse(
        buffer,
        headers={"Content-Disposition": f"attachment; filename={_csv_name}.csv"},
        media_type="text/csv",
    )
