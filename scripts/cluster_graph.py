import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.append(str(HERE / "../"))

from libs.lib_manejo_csv import lee_csv, lee_txt
from app.crud import cluster_graph, params
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


update_data_cluster_by_ppi(15900)
update_data_cluster_by_ppi(24275)
update_data_cluster_by_ppi(24267)
update_data_cluster_by_ppi(25433)
update_data_cluster_by_ppi(22989)
