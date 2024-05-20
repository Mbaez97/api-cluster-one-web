"""crud protein"""

from redis import Redis  # type: ignore
from app import schemas
from app.crud.crud_base import CRUDBase
from app.models import Protein, ClusterGraph, OverlappingProtein
from libs.lib_manejo_csv import lee_csv
from typing import List


class CRUDProtein(
    CRUDBase[Protein, schemas.ProteinCreate, schemas.ProteinUpdate]
):  # noqa
    # Mathods for get data from external sources
    uniprot_mappings_ids = {}  # type: ignore

    def get_mapping_to_uniprot_id(self) -> dict:
        """
        Returns a dictionary with the mapping from
        the SGD protein id to the UniprotKB id
        """
        for i in range(1, 18):
            _name = (
                "./uniprot_mapping/proteins_all_db_chunk"
                + str(i)
                + "_uniprot.csv"  # noqa: E501
            )  # noqa: E501
            try:
                _data = lee_csv(_name)
                for _prot in _data:
                    self.uniprot_mappings_ids[_prot[1]] = _prot[2]
            except Exception as e:
                print(e)
                pass
        return self.uniprot_mappings_ids

    def mapping_to_uniprot_id(self, proteins):
        _mapping = self.get_mapping_to_uniprot_id()
        _proteins = []
        for _prot in proteins:
            try:
                _proteins.append(_mapping[_prot])
            except Exception as e:
                print(e)
                pass
        return _proteins

    def update_redis(self, proteins: list) -> None:
        """Update redis"""
        _proteins = self.mapping_to_uniprot_id(proteins)
        r = Redis(host="cl1_redis", port=6379, db=3)
        for _prot in _proteins:
            print(_prot)
            r.sadd("proteins", _prot)

    # Get data from database
    def get_all(self, db) -> Protein:
        """Get all protein"""
        return db.query(Protein).all()

    def get_by_id(self, db, *, id: int) -> Protein:
        """Get protein by id"""
        return db.query(Protein).filter(Protein.id == id).first()

    def get_by_name(self, db, *, name: str) -> Protein:
        """Get agencia by name"""
        return db.query(Protein).filter(Protein.name == name).first()

    # Create data in database
    def quick_creation(self, db, *, name: str) -> Protein:
        _data = name
        _url = "www.ebi.ac.uk/proteins/api/proteins/proteins?protein=" + _data
        # TODO: Mapping to uniprot id

        protein_1 = Protein(  # type: ignore
            name=_data,
            description="Automatic node created from PPI file",
            url_info=_url + _data,
        )
        db.add(protein_1)
        db.commit()
        return protein_1

    def get_all_by_cluster(self, db, *, cluster_id: int) -> List[Protein]:
        """Get protein by cluster id"""
        _cluster = (
            db.query(ClusterGraph).filter(ClusterGraph.id == cluster_id).first()  # noqa
        )  # noqa
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
    CRUDBase[
        OverlappingProtein,
        schemas.OverlappingProteinCreate,
        schemas.OverlappingProteinUpdate,
    ]
):  # noqa
    def get_all(self, db) -> OverlappingProtein:
        """Get all protein"""
        return db.query(OverlappingProtein).all()

    def get_by_id(self, db, *, id: int) -> OverlappingProtein:
        """Get protein by id"""
        return db.query(OverlappingProtein).filter(OverlappingProtein.id == id).first()

    def get_by_name(self, db, *, name: str) -> OverlappingProtein:
        """Get agencia by name"""
        return (
            db.query(OverlappingProtein).filter(OverlappingProtein.name == name).first()
        )

    def quick_creation(self, db, *, name: str) -> OverlappingProtein:
        _data = name
        _url = "www.ebi.ac.uk/proteins/api/proteins/proteins?protein=" + _data

        protein_1 = OverlappingProtein(  # type: ignore
            name=_data,
            description="Automatic node created from PPI file",
            # score=0.0,
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
        return (
            db.query(OverlappingProtein)
            .filter(OverlappingProtein.id.in_(_proteins_id))
            .all()
        )


protein = CRUDProtein(Protein)
overlapping_protein = CRUDOverlappingProtein(OverlappingProtein)
