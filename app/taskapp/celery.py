from redis import Redis  # type: ignore
import json
from app import crud
from app.db.session import SessionLocal
from celery import Celery  # type: ignore
from config import settings
from libs.lib_manejo_csv import lee_txt

celery_app = Celery(
    __name__, broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND  # type: ignore # noqa
)


# tasks functions
@celery_app.task(name="app.taskapp.celery.test_celery")
def test_celery(word: str) -> str:
    print(f"Celery task: {word}")
    return f"test task return {word}"


@celery_app.task(name="app.taskapp.celery.async_creation_edge_for_cluster")
def async_creation_edge_for_cluster(
    ppi_id: int,
    cluster_id: int,
    cluster_edges: list,
) -> str:
    db = SessionLocal()
    for edge in cluster_edges:
        protein_a_id = edge["data"]["source"]
        protein_b_id = edge["data"]["target"]
        try:
            _edge_obj = crud.edge.get_by_proteins(
                db,
                protein_a_id=protein_a_id,
                protein_b_id=protein_b_id,
            )
            try:
                _weight = crud.edge.get_weight_edge_from_ppi(
                    db,
                    protein_a_id=protein_a_id,
                    protein_b_id=protein_b_id,
                    ppi_id=ppi_id,
                )
            except Exception as e:
                print(e)
                _weight = 1
            if not _edge_obj:
                crud.edge.create_edge_for_cluster(  # type: ignore
                    db,
                    obj={
                        "protein_a_id": protein_a_id,
                        "protein_b_id": protein_b_id,
                        "weight": _weight,
                        "direction": 1,
                        "refers_to": cluster_id,
                    },
                )
                print("LOGS: Edge created and added to cluster")
            else:
                # Validate if the edge is already in the cluster
                _edge_cluster = crud.edge.in_cluster(
                    db, obj={}, edge_id=_edge_obj.id, cluster_id=cluster_id
                )
                if not _edge_cluster:
                    crud.edge.add_edge_to_cluster(
                        db,
                        obj={
                            "id": _edge_obj.id,
                            "weight": _weight,
                            "refers_to": cluster_id,
                        },
                    )
                else:
                    print("LOGS: Edge already in cluster")
        except Exception as e:
            print(e)
        finally:
            db.close()
    return f"Celery task: async_creation_edge_for_cluster -> PPI: {ppi_id} - Cluster: {cluster_id} - Cant: {len(cluster_edges)}"  # noqa


@celery_app.task(name="app.taskapp.celery.async_insert_redis")
def async_insert_redis(
    ppi_id: int,
) -> str:
    db = SessionLocal()
    _ppi_obj = crud.ppi_graph.get_ppi_by_id(db, id=ppi_id)
    ppi_dataset = lee_txt(_ppi_obj.data)
    r = Redis(host="redis", port=6379, db=3)
    _objects = []
    for data in ppi_dataset:
        data = data.replace("\n", "")
        _data = data.split("\t")
        if len(_data) == 1:
            _data = data.split(" ")
        protein_1 = crud.protein.get_by_name(db, name=_data[0])
        protein_2 = crud.protein.get_by_name(db, name=_data[1])
        try:
            _weight = float(_data[2])
        except IndexError:
            _weight = 0.0
        except Exception as e:
            print(e)
            _weight = 0.0
        if not protein_1:
            protein_1 = crud.protein.quick_creation(db, name=_data[0])
        if not protein_2:
            protein_2 = crud.protein.quick_creation(db, name=_data[1])
        _redis_obj = {
            "key": f"{protein_1.id}-{protein_2.id}-{_ppi_obj.id}",
            "json": json.dumps(
                {
                    "protein_a": protein_1.name,
                    "protein_b": protein_2.name,
                    "weight": _weight,
                    "key": f"{protein_1.id}-{protein_2.id}-{_ppi_obj.id}",
                }
            ),
        }
        _objects.append(_redis_obj)
    r.mset({obj["key"]: obj["json"] for obj in _objects})
    r.close()
    db.close()
    return f"Celery task: async_insert_redis -> PPI: {ppi_id}"


@celery_app.task(name="app.taskapp.celery.async_creation_edge_for_ppi")
def async_creation_edge_for_ppi(
    ppi_id: int,
) -> str:
    db = SessionLocal()
    _ppi_obj = crud.ppi_graph.get_ppi_by_id(db, id=ppi_id)
    ppi_dataset = lee_txt(_ppi_obj.data, delimiter="\t")
    for data in ppi_dataset:
        data = data.replace("\n", "")
        _data = data.split("\t")
        if len(_data) == 1:
            _data = data.split(" ")
        protein_1 = crud.protein.get_by_name(db, name=_data[0])
        protein_2 = crud.protein.get_by_name(db, name=_data[1])
        try:
            _weight = float(_data[2])
        except Exception:
            _weight = 0.0
        if not protein_1:
            protein_1 = crud.protein.quick_creation(db, name=_data[0])
        if not protein_2:
            protein_2 = crud.protein.quick_creation(db, name=_data[1])
        _edge = crud.edge.get_by_proteins(
            db, protein_a_id=protein_1.id, protein_b_id=protein_2.id
        )
        if _edge:
            _obj = {
                "id": _edge.id,
                "refers_to": _ppi_obj,
                "weight": _weight,
            }
            crud.edge.add_edge_to_ppi(db, obj=_obj)
        else:
            _obj = {
                "protein_a_id": protein_1.id,
                "protein_b_id": protein_2.id,
                "weight": _weight,
                "refers_to": _ppi_obj,
                "direction": 0,
            }
            crud.edge.create_edge_for_ppi(db, obj=_obj)
    db.close()
    return f"Celery task: async_creation_edge_for_ppi -> PPI: {ppi_id}"
