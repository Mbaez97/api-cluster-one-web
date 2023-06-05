"""crud protein"""

from app import schemas
from app.crud.crud_base import CRUDBase
from app.models import PPIGraph, ClusterGraph

"""crud ppi graph"""
class CRUDPPIGraph(CRUDBase[PPIGraph, schemas.GraphCreate, schemas.GraphUpdate]):
    def get_all_ppi(self, db) -> PPIGraph:
        """Get all ppi"""
        return db.query(PPIGraph).all()

    def get_ppi_by_id(self, db, *, id: int) -> PPIGraph:
        """Get ppi by id"""
        return db.query(PPIGraph).filter(PPIGraph.id == id).first()


"""crud cluster graph"""
class CRUDClusterGraph(CRUDBase[ClusterGraph, schemas.GraphCreate, schemas.GraphUpdate]):
    def get_all_cluster(self, db) -> ClusterGraph:
        """Get all cluster"""
        return db.query(ClusterGraph).all()

    def get_cluster_by_id(self, db, *, id: int) -> ClusterGraph:
        """Get cluster by id"""
        return db.query(ClusterGraph).filter(ClusterGraph.id == id).first()
    
cluster_graph = CRUDClusterGraph(ClusterGraph)
ppi_graph = CRUDPPIGraph(PPIGraph)
