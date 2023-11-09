"""Execute ClusterOne algorithm and return the data in json format."""
import time
import random
import json

from fastapi import APIRouter, Depends, HTTPException, Query  # noqa F401 # type: ignore
from fastapi.responses import StreamingResponse  # noqa F401 # type: ignore
from sqlalchemy.orm import Session  # noqa F401 # type: ignore

from app.api import deps
from app import crud
from app.api.utils import execute_cluster_one
from uuid import uuid4
from app.models import Layout
from app.taskapp.celery import async_creation_edge_for_cluster
from app.api.api_v1.endpoints.graph import (  # noqa F401 # type: ignore
    get_weight_by_protein,
    get_weight_by_interactions_list,
)  # noqa F401 # type: ignore

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


def process_data(data):
    """
    This function process the data to add the protein complex node and edges
    """
    star_time = time.time()
    for i in range(len(data)):
        for j in range(len(data[i]["nodes"])):
            current_node_id = data[i]["nodes"][j]["data"]["id"]
            for k in range(len(data)):
                # Aca tenemos que evitar los duplicados
                if i == k:
                    continue
                overlapping_nodes = [
                    node
                    for node in data[k]["nodes"]
                    if node["data"]["id"] == current_node_id
                ]
                if len(overlapping_nodes) > 0:
                    protein_complex = data[k]
                    node_protein_complex = {
                        "data": {
                            "id": protein_complex["code"],
                            "label": f"COMPLEX - {protein_complex['code']}",
                            "overlapping": False,
                            "type": "proteinComplex",
                        }
                    }
                    data[i]["nodes"][j]["data"]["overlapping"] = True
                    data[i]["nodes"].append(node_protein_complex)
                    _edge_protein_complex = {
                        "data": {
                            "source": data[i]["nodes"][j]["data"]["id"],
                            "target": node_protein_complex["data"]["id"],
                            "label": "Overlapping",
                            "type": "overlapping",
                        }
                    }
                    data[i]["edges"].append(_edge_protein_complex)
    for cluster in data:
        interactions_cluster = []
        alternative_interactions = []
        pop_index_edges = []
        for edge in cluster["edges"]:
            if (
                edge["data"]["label"] == "Overlapping"
                or edge["data"]["label"] == ""  # noqa
            ):  # noqa
                edge["data"]["label"] = ""
                continue
            protein1_id = edge["data"]["source"]
            protein2_id = edge["data"]["target"]
            ppi_id = cluster["ppi_id"]
            _key = f"{protein1_id}-{protein2_id}-{ppi_id}"
            interactions_cluster.append(_key)
        _interactions = get_weight_by_interactions_list(interactions_cluster)
        if _interactions:
            # Exclude None values
            _interactions = [
                json.loads(interaction.decode("utf-8"))
                for interaction in _interactions
                if interaction
            ]
            for index, edge in enumerate(cluster["edges"]):
                if (
                    edge["data"]["label"] == "Overlapping"
                    or edge["data"]["label"] == ""
                ):  # noqa
                    edge["data"]["label"] = ""
                    continue
                protein1_id = edge["data"]["source"]
                protein2_id = edge["data"]["target"]
                ppi_id = cluster["ppi_id"]
                _key = f"{protein1_id}-{protein2_id}-{ppi_id}"
                _interaction = [
                    interaction
                    for interaction in _interactions
                    if interaction["key"] == _key
                ]
                if _interaction:
                    _interaction = _interaction[0]
                    if _interaction["weight"] == 0:
                        edge["data"]["label"] = ""
                    else:
                        edge["data"]["label"] = _interaction["weight"]
                else:
                    _inverse_key = f"{protein2_id}-{protein1_id}-{ppi_id}"
                    alternative_interactions.append(_inverse_key)
                    pop_index_edges.append(index)
            _alternative_interactions = get_weight_by_interactions_list(
                alternative_interactions
            )
            if _alternative_interactions:
                # Exclude None values
                _alternative_interactions = [
                    json.loads(interaction.decode("utf-8"))
                    for interaction in _alternative_interactions
                    if interaction
                ]
                for index, edge in enumerate(cluster["edges"]):
                    if index not in pop_index_edges:
                        continue
                    protein1_id = edge["data"]["source"]
                    protein2_id = edge["data"]["target"]
                    ppi_id = cluster["ppi_id"]
                    _key = f"{protein2_id}-{protein1_id}-{ppi_id}"
                    _interaction = [
                        interaction
                        for interaction in _alternative_interactions
                        if interaction["key"] == _key
                    ]
                    if _interaction:
                        # Sacar index del pop_index_edges
                        pop_index_edges.remove(index)
                        _interaction = _interaction[0]
                        if _interaction["weight"] == 0:
                            edge["data"]["label"] = ""
                        else:
                            edge["data"]["label"] = _interaction["weight"]
                    else:
                        edge["data"]["label"] = ""

        # Remove edges
        cluster["edges"] = [
            e
            for i, e in enumerate(cluster["edges"])
            if i not in pop_index_edges  # noqa
        ]
    end_time = time.time()
    print(f"LOGS: Processing data time: {(end_time - star_time):.4f} seconds")
    return data


# ClusterOne API
@router.post("/run/")
def run_cluster_one(
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
    cluster_one_execution_time = time.time()
    if not _params_obj:
        _params_obj = crud.params.create_params_logs(db, obj=_params)
        response = execute_cluster_one(_command, file_name=_file_name)
        print("LOGS: Params created")
    else:
        _exist_params = True
        print("LOGS: Params already exists")
        response = crud.cluster_graph.get_file_by_params(db, params_id=_params_obj.id)  # type: ignore # noqa
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
                    _edge = {
                        "data": {
                            "source": _protein1["data"]["id"],
                            "target": _protein2["data"]["id"],
                            "label": "0",
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
                "ppi_id": pp_id,
            }
        )
    if _exist_params:
        print("LOGS: Params already exists")
        response_data = process_data(_clusters)
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
        return response_data
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
    response_data = process_data(_clusters)
    end_time = time.time()
    print(
        f"LOGS: ClusterOne Execution Time: {(cluster_one_execution_time - start_time):.4f} seconds"  # noqa
    )
    print(f"LOGS: Protein Uses Time: {(_total_protein_uses_time):.4f} seconds")
    print(f"LOGS: Edge Uses Time: {(_total_edge_uses_time):.4f} seconds")
    print(f"LOGS: Total Execution Time: {(end_time - start_time):.4f} seconds")
    return response_data


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
