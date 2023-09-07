"""crud edge"""

from app import schemas
from app.crud.crud_base import CRUDBase
from app.models import Edge, EdgeClusterInteraction


class CRUDEdge(CRUDBase[Edge, schemas.EdgeCreate, schemas.EdgeUpdate]):
    def get_all_cluster(self, db) -> Edge:
        """Get all cluster"""
        return db.query(Edge).all()

    def create_edge_for_cluster(self, db, *, obj: dict) -> Edge:
        """Create cluster"""
        print("LOGS: Creating edge for cluster")
        db_obj = Edge(
            protein_a_id=obj["protein_a_id"],
            protein_b_id=obj["protein_b_id"],
            weight=obj["weight"],
            has_direction=obj["has_direction"],
            direction=obj["direction"],
        )
        interaction = EdgeClusterInteraction(
            edge_id=db_obj.id,
            cluster_graph_id=obj["refers_to"].id,
        )
        db.add(db_obj)
        db.add(interaction)
        db.commit()
        db.refresh(db_obj)
        return db_obj


Edge = CRUDEdge(Edge)
