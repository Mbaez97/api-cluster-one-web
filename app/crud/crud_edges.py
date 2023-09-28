"""crud edge"""

from app import schemas
from app.crud.crud_base import CRUDBase
from app.models import Edge, EdgeClusterInteraction, EdgePPIInteraction
from typing import List


class CRUDEdge(CRUDBase[Edge, schemas.EdgeCreate, schemas.EdgeUpdate]):
    def get_by_proteins(
        self, db, *, protein_a_id: int, protein_b_id: int
    ) -> Edge:  # noqa
        """Get edge by protein id"""
        return (
            db.query(Edge)
            .filter(Edge.protein_a_id == protein_a_id)
            .filter(Edge.protein_b_id == protein_b_id)
            .first()
        )

    def create_edge_for_cluster(self, db, *, obj: dict) -> Edge:
        """Create cluster"""
        db_obj = Edge(  # type: ignore
            protein_a_id=obj["protein_a_id"],
            protein_b_id=obj["protein_b_id"],
            direction=obj["direction"],
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        interaction = EdgeClusterInteraction(  # type: ignore
            edge_id=db_obj.id,
            weight=obj["weight"],
            cluster_graph_id=obj["refers_to"],
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        return db_obj

    def create_edge_for_ppi(self, db, *, obj: dict) -> Edge:
        """Create cluster"""
        db_obj = Edge(
            protein_a_id=obj["protein_a_id"],
            protein_b_id=obj["protein_b_id"],
            direction=obj["direction"],
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        interaction = EdgePPIInteraction(
            edge_id=db_obj.id,
            weight=obj["weight"],
            ppi_interaction_id=obj["refers_to"].id,
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        print(
            f"LOGS: {db_obj.id} - {obj['refers_to'].id} - {obj['weight']} - {db_obj.protein_a.name} - {db_obj.protein_b.name}"
        )
        return db_obj

    def bulk_create_edge_for_cluster(
        self, db, *, obj: dict, edge_list: List[dict], cluster_id: int
    ) -> bool:
        # Creamos de una
        try:
            _edges_list = []
            for edge in edge_list:
                _edges_list.append(
                    {
                        "protein_a_id": edge["protein_a_id"],
                        "protein_b_id": edge["protein_b_id"],
                        "direction": edge["direction"],
                    }
                )
            data_edges = db.bulk_insert_mappings(Edge, _edges_list)
            db.commit()
            db.refresh(data_edges)
            _interactions = []
            for edge in edge_list:
                _edge_obj = self.get_by_proteins(
                    db,
                    protein_a_id=edge["protein_a_id"],
                    protein_b_id=edge["protein_b_id"],
                )
                _interactions.append(
                    {
                        "edge_id": _edge_obj.id,
                        "cluster_graph_id": cluster_id,
                        "weight": edge["weight"],
                    }
                )
            db.bulk_insert_mappings(EdgeClusterInteraction, _interactions)
            db.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def bulk_create_edge_for_ppi(
        self, db, *, obj: dict, edge_list: List[dict], ppi_id: int
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
                        "ppi_interaction_id": ppi_id,
                        "weight": 1,
                    }
                )
            db.bulk_insert_mappings(EdgePPIInteraction, _interactions)
            db.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def add_edge_to_cluster(self, db, *, obj: dict):
        """Create cluster"""
        interaction = EdgeClusterInteraction(  # type: ignore
            edge_id=obj["id"],
            cluster_graph_id=obj["refers_to"],
            weight=obj["weight"],
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        return obj

    def add_edge_to_ppi(self, db, *, obj: dict) -> Edge:
        """Create cluster"""
        db_obj = db.query(Edge).filter(Edge.id == obj["id"]).first()
        interaction = EdgePPIInteraction(
            edge_id=db_obj.id,
            ppi_interaction_id=obj["refers_to"].id,
            weight=obj["weight"],
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        print(
            f"LOGS: {db_obj.id} - {obj['refers_to'].id} - {obj['weight']} - {db_obj.protein_a.name} - {db_obj.protein_b.name}"
        )
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
                        "edge_id": edge["obj"].id,
                        "cluster_graph_id": cluster_id,
                        "weight": edge["weight"],
                    }
                )
            db.bulk_insert_mappings(EdgeClusterInteraction, _interactions)
            db.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def bulk_add_edge_to_ppi(
        self, db, *, obj: dict, edge_list: List[Edge], ppi_id: int
    ) -> bool:
        # Creamos de una
        try:
            _interactions = []
            for edge in edge_list:
                _interactions.append(
                    {
                        "edge_id": edge.id,
                        "ppi_graph_id": ppi_id,
                        "weight": 1,
                    }
                )
            db.bulk_insert_mappings(EdgePPIInteraction, _interactions)
            db.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def get_edge_from_ppi(
        self,
        db,
        *,
        obj: dict,
        ppi_id: int,
        protein_a_id: int = 0,
        protein_b_id: int = 0,
    ):
        """
        Get Edge from PPI
        """
        if protein_a_id != 0 and protein_b_id != 0:
            return (
                db.query(Edge)
                .join(EdgePPIInteraction)
                .filter(Edge.protein_a_id == protein_a_id)
                .filter(Edge.protein_b_id == protein_b_id)
                .filter(EdgePPIInteraction.ppi_interaction_id == ppi_id)
                .first()
            )
        else:
            return (
                db.query(Edge)
                .join(EdgePPIInteraction)
                .filter(EdgePPIInteraction.ppi_interaction_id == ppi_id)
                .all()
            )

    def get_weight_edge_from_ppi(
        self,
        db,
        *,
        ppi_id: int,
        protein_a_id: int = 0,
        protein_b_id: int = 0,
    ):
        """
        Get Edge from PPI
        """
        if protein_a_id != 0 and protein_b_id != 0:
            _edge = self.get_by_proteins(
                db,
                protein_a_id=protein_a_id,
                protein_b_id=protein_b_id,
            )
            _interaction = (
                db.query(EdgePPIInteraction)
                .filter(EdgePPIInteraction.ppi_interaction_id == ppi_id)
                .filter(EdgePPIInteraction.edge_id == _edge.id)
                .first()
            )
            if _interaction:
                return _interaction.weight
            return 0
        else:
            return 0

    def get_edge_from_cluster(
        self,
        db,
        *,
        obj: dict,
        cluster_id: int,
        protein_a_id: int = 0,
        protein_b_id: int = 0,
    ):
        """
        Get Edge from Cluster
        """
        if protein_a_id != 0 and protein_b_id != 0:
            return (
                db.query(Edge)
                .join(EdgeClusterInteraction)
                .filter(Edge.protein_a_id == protein_a_id)
                .filter(Edge.protein_b_id == protein_b_id)
                .filter(EdgeClusterInteraction.cluster_graph_id == cluster_id)
                .first()
            )
        else:
            return (
                db.query(Edge)
                .join(EdgeClusterInteraction)
                .filter(EdgeClusterInteraction.cluster_graph_id == cluster_id)
                .all()
            )

    def in_cluster(self, db, *, obj: dict, cluster_id: int, edge_id: int = 0):
        """
        Get Edge from Cluster
        """
        return (
            db.query(Edge)
            .join(EdgeClusterInteraction)
            .filter(EdgeClusterInteraction.cluster_graph_id == cluster_id)
            .filter(Edge.id == edge_id)
            .first()
        )


edge = CRUDEdge(Edge)
