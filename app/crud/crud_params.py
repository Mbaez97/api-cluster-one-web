"""crud protein"""

from app import schemas
from app.crud.crud_base import CRUDBase
from app.models import ClusterOneLogParams, ClusterGraph
from typing import List


class CRUDClusterOneLogParams(
    CRUDBase[ClusterOneLogParams, schemas.ParamsCreate, schemas.ParamsUpdate]
):  # noqa
    def get_all(self, db) -> ClusterOneLogParams:
        """Get all protein"""
        return db.query(ClusterOneLogParams).all()

    def get_by_id(self, db, *, id: int) -> ClusterOneLogParams:
        """Get protein by id"""
        return (
            db.query(ClusterOneLogParams).filter(ClusterOneLogParams.id == id).first()  # type: ignore  # noqa
        )

    def get_clusters_by_log_id(self, db, *, id: int) -> List[ClusterGraph]:
        """Get clusters by log id"""
        return (
            db.query(ClusterGraph)
            .filter(ClusterGraph.cluster_one_log_params_id == id)
            .all()
        )

    def get_by_elements(self, db, *, obj: dict) -> ClusterOneLogParams:
        """Get or create cluster"""

        db_obj = (
            db.query(ClusterOneLogParams)
            .filter(ClusterOneLogParams.min_size == obj["min_size"])
            .filter(ClusterOneLogParams.min_density == obj["min_density"])
            .filter(ClusterOneLogParams.max_overlap == obj["max_overlap"])
            .filter(ClusterOneLogParams.penalty == obj["penalty"])
            .filter(ClusterOneLogParams.ppi_graph_id == obj["ppi_graph_id"])
            .first()
        )
        return db_obj

    def create_params_logs(self, db, *, obj: dict) -> ClusterOneLogParams:
        """Create cluster"""
        db_obj = ClusterOneLogParams(  # type: ignore
            min_size=obj["min_size"],
            min_density=obj["min_density"],
            max_overlap=obj["max_overlap"],
            penalty=obj["penalty"],
            ppi_graph_id=obj["ppi_graph_id"],
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


params = CRUDClusterOneLogParams(ClusterOneLogParams)
