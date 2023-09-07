"""Assigns Raspadita box, libro and cartones"""
import time

import random


from fastapi import APIRouter, Depends, HTTPException, Query
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
@router.post("/run/")
def run_cluester_one(
    db: Session = Depends(deps.get_db),
    pp_id: int = Query(None, description="PPI ID", gt=0),
    size: int = Query(None, description="Size of clusters", gt=0),
    density: float = Query(None, description="Density of clusters", gt=0),
):
    """
    Get All Cluster data from ClusterOne
    """
    # if not cluster_one_version:
    #     _base_command = "java -jar cluster_one-1.0.jar"
    # else:
    # _base_command = f"java -jar cluster_one-{cluster_one_version}.jar"
    start_time = time.time()
    _base_command = "java -jar cluster_one-1.0.jar"
    _file_name = f"complex_cluster_response_{get_default_uuid()}.csv"
    _final_command = "> " + _file_name
    if not pp_id:
        raise HTTPException(status_code=404, detail="PPI not found")
    ppi_obj = crud.ppi_graph.get_ppi_by_id(db, id=pp_id)
    if not ppi_obj:
        raise HTTPException(status_code=404, detail="PPI not found")
    _command = f"{_base_command} {ppi_obj.data} -F csv {_final_command}"
    if size:
        _command = _command + f" -s {size}"
    if density:
        _command = _command + f" -d {density}"
    response = execute_cluster_one(_command, file_name=_file_name)
    cluster_one_execution_time = time.time()
    _clusters = []
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
                _protein_obj = crud.protein.quick_creation(db, name=protein)
            _protein_node = {
                "data": {
                    "id": _protein_obj.id,
                    "label": _protein_obj.name,
                    "type": "protein",
                },
            }
            _proteins_obj.append(_protein_node)
        _edges_to_create_in_cluster = []
        _edges_to_add_in_cluster = []
        for _protein in _proteins_obj:
            for _protein2 in _proteins_obj:
                if _protein["data"]["id"] != _protein2["data"]["id"]:
                    _edge = {
                        "data": {
                            "source": _protein["data"]["id"],
                            "target": _protein2["data"]["id"],
                            "label": "1",
                        },
                    }
                    _edges.append(_edge)
                    _edge_obj = crud.edge.get_by_proteins(
                        db,
                        protein_a_id=_protein["data"]["id"],
                        protein_b_id=_protein2["data"]["id"],
                    )
                    if not _edge_obj:
                        _edges_to_create_in_cluster.append(
                            {
                                "protein_a_id": _protein["data"]["id"],
                                "protein_b_id": _protein2["data"]["id"],
                                "weight": 1,
                                "has_direction": False,
                                "direction": 0,
                            }
                        )
                    else:
                        _edges_to_add_in_cluster.append(_edge_obj)
        _clusters.append(
            {
                "code": str(_cluster_obj.id),
                "size": _cluster_obj.size,
                "density": _cluster_obj.density,
                "internal_weight": _cluster_obj.internal_weight,
                "external_weight": _cluster_obj.external_weight,
                "quantity": _cluster_obj.quality,
                "nodes": _proteins_obj,
                "edges": _edges,
            }
        )
        if _edges_to_create_in_cluster:
            crud.edge.bulk_create_edge_for_cluster(
                db,
                obj={},
                edge_list=_edges_to_create_in_cluster,
                cluster_id=_cluster_obj.id,
            )
        if _edges_to_add_in_cluster:
            crud.edge.bulk_add_edge_to_cluster(
                db,
                obj={},
                edge_list=_edges_to_add_in_cluster,
                cluster_id=_cluster_obj.id,
            )
    print("DONE!")
    end_time = time.time()
    print(
        f"ClusterOne Execution Time: {(cluster_one_execution_time - start_time):.4f} seconds"
    )
    print(f"Total Execution Time: {(end_time - start_time):.4f} seconds")
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
