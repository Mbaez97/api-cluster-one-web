from celery import Celery  # type: ignore

from config import settings
from app import crud
from app.db.session import SessionLocal

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
    protein_a_id: int,
    protein_b_id: int,
    ppi_id: int,
    cluster_id: int,
) -> str:
    db = SessionLocal()
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
                print("LOGS: Edge added to cluster")
            else:
                print("LOGS: Edge already in cluster")
    except Exception as e:
        print(e)
    finally:
        db.close()
    return f"Celery task: async_creation_edge_for_cluster {cluster_id} - {protein_a_id} - {protein_b_id} - {ppi_id}"  # noqa
