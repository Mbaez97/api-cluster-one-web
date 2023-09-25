"""crud protein"""

from app import schemas
from app.crud.crud_base import CRUDBase
from app.models import Protein, ClusterGraph, OverlappingProtein
from typing import List


class CRUDProtein(
    CRUDBase[Protein, schemas.ProteinCreate, schemas.ProteinUpdate]
):  # noqa
    def get_all(self, db) -> Protein:
        """Get all protein"""
        return db.query(Protein).all()

    def get_by_id(self, db, *, id: int) -> Protein:
        """Get protein by id"""
        return db.query(Protein).filter(Protein.id == id).first()

    def get_by_name(self, db, *, name: str) -> Protein:
        """Get agencia by name"""
        return db.query(Protein).filter(Protein.name == name).first()

    def quick_creation(self, db, *, name: str) -> Protein:
        _data = name
        _url = "www.ebi.ac.uk/proteins/api/proteins/"

        protein_1 = Protein(
            name=_data,
            description="Automatic node created from PPI file",
            score=0.0,
            url_info=_url + _data,
        )
        db.add(protein_1)
        db.commit()
        print("Protein created: ", protein_1.name)
        return protein_1

    def get_all_by_cluster(self, db, *, cluster_id: int) -> List[Protein]:
        """Get protein by cluster id"""
        _cluster = db.query(ClusterGraph).filter(ClusterGraph.id == cluster_id).first()
        _edges = _cluster.edges
        _proteins_a_id = [i.protein_a_id for i in _edges]
        _proteins_b_id = [i.protein_b_id for i in _edges]
        _proteins_id = []
        for i in _proteins_a_id:
            if i not in _proteins_id:
                _proteins_id.append(i)
        for i in _proteins_b_id:
            if i not in _proteins_id:
                _proteins_id.append(i)
        return db.query(Protein).filter(Protein.id.in_(_proteins_id)).all()


class CRUDOverlappingProtein(
    CRUDBase[OverlappingProtein, schemas.OverlappingProteinCreate, schemas.OverlappingProteinUpdate]
):  # noqa
    def get_all(self, db) -> OverlappingProtein:
        """Get all protein"""
        return db.query(OverlappingProtein).all()

    def get_by_id(self, db, *, id: int) -> OverlappingProtein:
        """Get protein by id"""
        return db.query(OverlappingProtein).filter(OverlappingProtein.id == id).first()

    def get_by_name(self, db, *, name: str) -> OverlappingProtein:
        """Get agencia by name"""
        return db.query(OverlappingProtein).filter(OverlappingProtein.name == name).first()

    def quick_creation(self, db, *, name: str) -> OverlappingProtein:
        _data = name
        _url = "www.ebi.ac.uk/proteins/api/proteins/"

        protein_1 = OverlappingProtein(
            name=_data,
            description="Automatic node created from PPI file",
            score=0.0,
            url_info=_url + _data,
        )
        db.add(protein_1)
        db.commit()
        print("Protein created: ", protein_1.name)
        return protein_1

    def get_all_by_cluster(self, db, *, cluster_id: int) -> List[OverlappingProtein]:
        """Get protein by cluster id"""
        _cluster = db.query(ClusterGraph).filter(ClusterGraph.id == cluster_id).first()
        _edges = _cluster.edges
        _proteins_a_id = [i.protein_a_id for i in _edges]
        _proteins_b_id = [i.protein_b_id for i in _edges]
        _proteins_id = []
        for i in _proteins_a_id:
            if i not in _proteins_id:
                _proteins_id.append(i)
        for i in _proteins_b_id:
            if i not in _proteins_id:
                _proteins_id.append(i)
        return db.query(OverlappingProtein).filter(OverlappingProtein.id.in_(_proteins_id)).all()

protein = CRUDProtein(Protein)
