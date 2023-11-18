import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.append(str(HERE / "../"))

from libs.lib_manejo_csv import lee_csv, lee_txt
from app.crud import cluster_graph, params, enrichment
from app.db.session import SessionLocal

from config import Settings

settings = Settings()
print(settings.SQLALCHEMY_DATABASE_URI)

DATA_MAPPING = {
    "15900": "/app/app/media/clusters/cluster_collins.csv",
    "24275": "/app/app/media/clusters/cluster_gavin2006.csv",
    "24267": "/app/app/media/clusters/cluster_krogan2006kore.csv",
    "25433": "/app/app/media/clusters/cluster_krogan2006extend.csv",
    "22989": "/app/app/media/clusters/cluster_biogrid.csv",
}


def update_data_cluster_by_ppi(ppi_id: int):
    """
    Updates the data of all clusters associated with a given PPI graph ID.

    Args:
        ppi_id (int): The ID of the PPI graph.

    Returns:
        str: A message indicating that all clusters have been updated to the given PPI ID.
    """
    db = SessionLocal()
    obj_params = {
        "min_size": None,
        "min_density": None,
        "max_overlap": None,
        "penalty": None,
        "ppi_graph_id": ppi_id,
    }
    params_obj = params.get_by_elements(db, obj=obj_params)
    clusters = params.get_clusters_by_log_id(db, id=params_obj.id)
    for cluster in clusters:
        cluster.data = DATA_MAPPING[str(ppi_id)]
        db.add(cluster)
        db.commit()
        db.refresh(cluster)

    return f"Update all clusters to {ppi_id}"


# update_data_cluster_by_ppi(15900)
# update_data_cluster_by_ppi(24275)
# update_data_cluster_by_ppi(24267)
# update_data_cluster_by_ppi(25433)
# update_data_cluster_by_ppi(22989)


def populate_ora_score():
    """
    Populate the ORA score for all clusters.
    """
    db = SessionLocal()
    _cl_params = params.get_all(db)
    print(f"Total de CL1 parametros: {len(_cl_params)}")
    for param in _cl_params:
        _clusters = params.get_clusters_by_log_id(db, id=param.id)
        _cantidad_total = len(_clusters)
        _bp_clusters = []
        _mf_clusters = []
        _cc_clusters = []
        print(f"Total de clusters: {_cantidad_total}")
        for _cluster in _clusters:
            _enrichments = enrichment.get_by_cluster_id(
                db, cluster_id=_cluster.id
            )  # noqa
            for _enrichment in _enrichments:
                if (
                    _enrichment.go_terms.domain == "BP"
                    and _enrichment.p_value < 0.05  # noqa
                ):  # noqa
                    if _cluster not in _bp_clusters:
                        _bp_clusters.append(_cluster)
                elif (
                    _enrichment.go_terms.domain == "MF"
                    and _enrichment.p_value < 0.05  # noqa
                ):  # noqa
                    if _cluster not in _mf_clusters:
                        _mf_clusters.append(_cluster)
                elif (
                    _enrichment.go_terms.domain == "CC"
                    and _enrichment.p_value < 0.05  # noqa
                ):  # noqa
                    if _cluster not in _cc_clusters:
                        _cc_clusters.append(_cluster)
        _cantidad_clusters_bp = len(_bp_clusters)
        _cantidad_clusters_mf = len(_mf_clusters)
        _cantidad_clusters_cc = len(_cc_clusters)
        print(f"Total de clusters BP: {_cantidad_clusters_bp}")
        print(f"Total de clusters MF: {_cantidad_clusters_mf}")
        print(f"Total de clusters CC: {_cantidad_clusters_cc}")
        obj = {
            "ora_bp_score": _cantidad_clusters_bp / _cantidad_total,
            "ora_mf_score": _cantidad_clusters_mf / _cantidad_total,
            "ora_cc_score": _cantidad_clusters_cc / _cantidad_total,
        }
        params.update(db, db_obj=param, obj_in=obj)
        print(f"Actualizado: {param.id}")
    print("Finalizado")


populate_ora_score()
