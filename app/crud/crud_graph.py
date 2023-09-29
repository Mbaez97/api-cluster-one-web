"""crud protein"""

from app import schemas
from app.crud.crud_base import CRUDBase
from app.models import PPIGraph, ClusterGraph

"""crud ppi graph"""


class CRUDPPIGraph(CRUDBase[PPIGraph, schemas.GraphCreate, schemas.GraphUpdate]):  # type: ignore # noqa
    def get_all_ppi(self, db) -> PPIGraph:
        """Get all ppi"""
        return db.query(PPIGraph).all()

    def get_ppi_by_id(self, db, *, id: int) -> PPIGraph:
        """Get ppi by id"""
        return db.query(PPIGraph).filter(PPIGraph.id == id).first()

    def get_ppi_by_name(self, db, *, name: str) -> PPIGraph:
        """Get ppi by name"""
        return db.query(PPIGraph).filter(PPIGraph.name == name).first()

    def create_ppi_from_file(self, db, *, obj: dict) -> PPIGraph:
        """Create ppi from file"""
        db_obj = PPIGraph(  # type: ignore
            size=obj["size"],
            layout=obj["layout"],
            data=obj["data"],
            name=obj["name"],
            preloaded=obj["preloaded"],
            density=obj["density"],
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


"""crud cluster graph"""


class CRUDClusterGraph(
    CRUDBase[ClusterGraph, schemas.GraphCreate, schemas.GraphUpdate]
):
    def get_all_cluster(self, db) -> ClusterGraph:
        """Get all cluster"""
        return db.query(ClusterGraph).all()

    def get_cluster_by_id(self, db, *, id: int) -> ClusterGraph:
        """Get cluster by id"""
        return db.query(ClusterGraph).filter(ClusterGraph.id == id).first()

    def get_cluster_by_elements(self, db, *, obj: dict) -> ClusterGraph:
        """Get cluster by elements"""
        return (
            db.query(ClusterGraph)
            .filter(ClusterGraph.external_weight == obj["external_weight"])
            .filter(ClusterGraph.internal_weight == obj["internal_weight"])
            .filter(ClusterGraph.density == obj["density"])
            .filter(ClusterGraph.size == obj["size"])
            .filter(ClusterGraph.quality == obj["quality"])
            .filter(ClusterGraph.p_value == obj["p_value"])
            .filter(
                ClusterGraph.cluster_one_log_params_id
                == obj["cluster_one_log_params_id"]
            )
            .first()
        )

    def create_cluster(self, db, *, obj: dict) -> ClusterGraph:
        """Create cluster"""
        db_obj = ClusterGraph(  # type: ignore
            external_weight=obj["external_weight"],
            internal_weight=obj["internal_weight"],
            density=obj["density"],
            size=obj["size"],
            quality=obj["quality"],
            p_value=obj["p_value"],
            layout=obj["layout"],
            data=obj["data"],
            cluster_one_log_params_id=obj["cluster_one_log_params_id"],
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


cluster_graph = CRUDClusterGraph(ClusterGraph)
ppi_graph = CRUDPPIGraph(PPIGraph)
