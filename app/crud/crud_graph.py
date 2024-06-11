from app import schemas
from app.crud.crud_base import CRUDBase
from app.models import PPIGraph, ClusterGraph, Layout
from libs.lib_manejo_csv import lee_csv


# CRUD Layout
class CRUDLayout(CRUDBase[Layout, schemas.LayoutCreate, schemas.LayoutUpdate]):
    def get_all_layout(self, db) -> Layout:
        """Get all layout"""
        return db.query(Layout).all()

    def get_layout_by_id(self, db, *, id: int) -> Layout:
        """Get layout by id"""
        return db.query(Layout).filter(Layout.id == id).first()

    def quick_create_layout(self, db, *, obj: dict) -> Layout:
        """Quick create layout"""
        db_obj = Layout(  # type: ignore
            name=obj["name"],
            animated=obj["animated"],
            node_spacing=obj["node_spacing"],
            randomize=obj["randomize"],
            max_simulation_time=obj["max_simulation_time"],
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


# CRUD PPI Graph
class CRUDPPIGraph(CRUDBase[PPIGraph, schemas.GraphCreate, schemas.GraphUpdate]):  # type: ignore # noqa
    def get_all_ppi(self, db) -> PPIGraph:
        """Get all ppi"""
        return db.query(PPIGraph).all()

    def get_all_preloaded_ppi(self, db) -> PPIGraph:
        """Get all preloaded ppi"""
        return db.query(PPIGraph).filter(PPIGraph.preloaded == True).all()

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


# CRUD Cluster Graph
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

    def get_clusters_by_params(self, db, *, params_id: int) -> list:
        """Get clusters by params"""
        return (
            db.query(ClusterGraph)
            .filter(ClusterGraph.cluster_one_log_params_id == params_id)
            .all()
        )

    def get_cluster_by_params_by_file_id(
        self, db, *, params_id: int, file_id: int
    ) -> ClusterGraph:
        """Get cluster by params"""
        return (
            db.query(ClusterGraph)
            .filter(ClusterGraph.cluster_one_log_params_id == params_id)
            .filter(ClusterGraph.data_file_id == file_id)
            .first()
        )

    def get_proteins_by_cluster(self, db, *, id: int) -> list:
        """Get proteins by cluster"""
        cluster = db.query(ClusterGraph).filter(ClusterGraph.id == id).all()
        edges = cluster[0].edges
        proteins = []
        for edge in edges:
            if edge.protein_a not in proteins:
                proteins.append(edge.protein_a)
            if edge.protein_b not in proteins:
                proteins.append(edge.protein_b)
        return proteins

    def get_file_by_params(self, db, *, params_id: int) -> list:
        """Get file by params"""
        _cluster = (
            db.query(ClusterGraph)
            .filter(ClusterGraph.cluster_one_log_params_id == params_id)
            .first()
        )
        _file_path = _cluster.data
        return lee_csv(_file_path)

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
            data_file_id=obj["data_file_id"],
            cluster_one_log_params_id=obj["cluster_one_log_params_id"],
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


cluster_graph = CRUDClusterGraph(ClusterGraph)
ppi_graph = CRUDPPIGraph(PPIGraph)
layout = CRUDLayout(Layout)
