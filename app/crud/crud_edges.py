"""crud edge"""

from app import schemas
from app.crud.crud_base import CRUDBase
from app.models import Edge, EdgeClusterInteraction
from typing import List


class CRUDEdge(CRUDBase[Edge, schemas.EdgeCreate, schemas.EdgeUpdate]):
    def get_by_proteins(self, db, *, protein_a_id: int, protein_b_id: int) -> Edge:
        """Get edge by protein id"""
        return (
            db.query(Edge)
            .filter(Edge.protein_a_id == protein_a_id)
            .filter(Edge.protein_b_id == protein_b_id)
            .first()
        )

    def create_edge_for_cluster(self, db, *, obj: dict) -> Edge:
        """Create cluster"""
        db_obj = Edge(
            protein_a_id=obj["protein_a_id"],
            protein_b_id=obj["protein_b_id"],
            direction=obj["direction"],
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        interaction = EdgeClusterInteraction(
            edge_id=db_obj.id,
            weight=obj["weight"],
            cluster_graph_id=obj["refers_to"].id,
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        return db_obj

    def bulk_create_edge_for_cluster(
        self, db, *, obj: dict, edge_list: List[dict], cluster_id: int
    ) -> bool:
        # Creamos de una
        try:
            data_edges = db.bulk_insert_mappings(Edge, edge_list)
            db.commit()
            db.refresh(data_edges)
            _interactions = []
            for edge in edge_list:
                _interactions.append(
                    {
                        "edge_id": edge.id,
                        "cluster_graph_id": cluster_id,
                        "weight": 1,
                    }
                )
            db.bulk_insert_mappings(EdgeClusterInteraction, _interactions)
            db.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def add_edge_to_cluster(self, db, *, obj: dict) -> Edge:
        """Create cluster"""
        db_obj = db.query(Edge).filter(Edge.id == obj["id"]).first()
        interaction = EdgeClusterInteraction(
            edge_id=db_obj.id,
            cluster_graph_id=obj["refers_to"].id,
            weight=obj["weight"],
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        return db_obj

    def bulk_add_edge_to_cluster(
        self, db, *, obj: dict, edge_list: List[Edge], cluster_id: int
    ) -> bool:
        # Creamos de una
        try:
            _interactions = []
            for edge in edge_list:
                _interactions.append(
                    {
                        "edge_id": edge.id,
                        "cluster_graph_id": cluster_id,
                        "weight": 1,
                    }
                )
            db.bulk_insert_mappings(EdgeClusterInteraction, _interactions)
            db.commit()
            return True
        except Exception as e:
            print(e)
            return False


edge = CRUDEdge(Edge)
