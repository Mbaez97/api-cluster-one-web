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
from app.taskapp.celery import test_celery, async_creation_edge_for_cluster


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


def edge_exists(protein1_id: int, protein2_id: int, _edges: list):
    """Verifica si un arco ya existe entre dos nodos."""
    for edge in _edges:
        source, target = edge["data"]["source"], edge["data"]["target"]
        if (source == protein1_id and target == protein2_id) or (
            source == protein2_id and target == protein1_id
        ):
            return True
    return False


# ClusterOne API
@router.post("/run/")
def run_cluester_one(
    db: Session = Depends(deps.get_db),
    pp_id: int = Query(None, description="PPI ID", gt=0),
    min_size: int = Query(None, description="Size of clusters", gt=0),
    min_density: float = Query(None, description="Density of clusters", gt=0),
    max_overlap: float = Query(
        None, description="Max overlap of clusters", gt=0
    ),  # noqa
    penalty: float = Query(None, description="Penalty of clusters", gt=0),
):
    """
    Get All Cluster data from ClusterOne
    """
    # if not cluster_one_version:
    #     _base_command = "java -jar cluster_one-1.0.jar"
    # else:
    # _base_command = f"java -jar cluster_one-{cluster_one_version}.jar"

    start_time = time.time()
    if not pp_id:
        raise HTTPException(status_code=404, detail="PPI not found")
    ppi_obj = crud.ppi_graph.get_ppi_by_id(db, id=pp_id)
    if not ppi_obj:
        raise HTTPException(status_code=404, detail="PPI not found")

    _base_command = "java -jar cluster_one-1.0.jar"
    _file_name = f"complex_cluster_response_{get_default_uuid()}.csv"
    _final_command = "> " + _file_name
    _command = f"{_base_command} {ppi_obj.data} -F csv {_final_command}"
    if min_size:
        _command = _command + f" -s {min_size}"
    if min_density:
        _command = _command + f" -d {min_density}"
    if max_overlap:
        _command = _command + f" --max-overlap {max_overlap}"
    if penalty:
        _command = _command + f" --penalty {penalty}"
    _params = {
        "min_size": min_size,
        "min_density": min_density,
        "max_overlap": max_overlap,
        "penalty": penalty,
        "ppi_graph_id": pp_id,
    }
    _params_obj = crud.params.get_by_elements(db, obj=_params)
    _exist_params = False
    if not _params_obj:
        _params_obj = crud.params.create_params_logs(db, obj=_params)
        print("LOGS: Params created")
    else:
        _exist_params = True
    response = execute_cluster_one(_command, file_name=_file_name)
    cluster_one_execution_time = time.time()
    _clusters = []
    _total_protein_uses_time = 0
    _total_edge_uses_time = 0
    print("LOGS: Get or Creating clusters in DB")
    for complex in response:
        _layout = db.query(Layout).filter(Layout.name == "random").first()
        _obj = {
            "size": complex[1],
            "density": complex[2],
            "internal_weight": complex[3],
            "external_weight": complex[4],
            "quality": complex[5],
            "p_value": complex[6],
            "layout": _layout,
            "data": "/app/app/media/clusters/" + _file_name,
            "cluster_one_log_params_id": _params_obj.id,
        }

        if _exist_params:
            _cluster_obj = crud.cluster_graph.get_cluster_by_elements(db, obj=_obj)
            if not _cluster_obj:
                _cluster_obj = crud.cluster_graph.create_cluster(db, obj=_obj)
        else:
            _cluster_obj = crud.cluster_graph.create_cluster(db, obj=_obj)
        # Proteins
        _initial_protein_uses_time = time.time()
        _proteins_obj = []
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
                    "overlapping": False,
                },
            }
            _proteins_obj.append(_protein_node)
        _protein_uses_time = time.time()
        _total_protein_uses_time += (  # type: ignore
            _protein_uses_time - _initial_protein_uses_time
        )  # noqa

        # Edges
        _initial_edge_uses_time = time.time()
        _edges = []  # type: ignore
        for i in range(len(_proteins_obj)):
            for j in range(i + 1, len(_proteins_obj)):
                _protein1 = _proteins_obj[i]
                _protein2 = _proteins_obj[j]

                # Verificar si el arco ya existe.
                if not edge_exists(
                    _protein1["data"]["id"], _protein2["data"]["id"], _edges
                ):
                    _weight = 1
                    _edge = {
                        "data": {
                            "source": _protein1["data"]["id"],
                            "target": _protein2["data"]["id"],
                            "label": f"{_weight}",
                        },
                    }
                    _edges.append(_edge)
        _edge_uses_time = time.time()
        _total_edge_uses_time += (  # type: ignore
            _edge_uses_time - _initial_edge_uses_time
        )  # noqa # type: ignore

        _clusters.append(
            {
                "code": str(_cluster_obj.id),
                "size": _cluster_obj.size,
                "density": _cluster_obj.density,
                "quality": _cluster_obj.quality,
                "p_value": _cluster_obj.p_value,
                "nodes": _proteins_obj,
                "edges": _edges,
            }
        )
    if _exist_params:
        print("LOGS: Params already exists")
        end_time = time.time()
        print(
            f"LOGS: ClusterOne Execution Time: {(cluster_one_execution_time - start_time):.4f} seconds"  # noqa
        )
        print(
            f"LOGS: Protein Uses Time: {(_total_protein_uses_time):.4f} seconds"  # noqa
        )  # noqa
        print(f"LOGS: Edge Uses Time: {(_total_edge_uses_time):.4f} seconds")
        print(
            f"LOGS: Total Execution Time: {(end_time - start_time):.4f} seconds"  # noqa
        )  # noqa
        return _clusters
    print("LOGS: Creating edges in DB")
    for _cluster in _clusters:
        # Async Create edge for cluster
        # async_creation_edge_for_cluster.delay(
        #     cluster_edges=_cluster["edges"],
        #     ppi_id=pp_id,
        #     cluster_id=_cluster["code"],
        # )
        async_creation_edge_for_cluster.apply_async(
            kwargs={
                "cluster_edges": _cluster["edges"],
                "ppi_id": pp_id,
                "cluster_id": _cluster["code"],
            },
        )
    end_time = time.time()
    print(
        f"LOGS: ClusterOne Execution Time: {(cluster_one_execution_time - start_time):.4f} seconds"  # noqa
    )
    print(f"LOGS: Protein Uses Time: {(_total_protein_uses_time):.4f} seconds")
    print(f"LOGS: Edge Uses Time: {(_total_edge_uses_time):.4f} seconds")
    print(f"LOGS: Total Execution Time: {(end_time - start_time):.4f} seconds")
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
