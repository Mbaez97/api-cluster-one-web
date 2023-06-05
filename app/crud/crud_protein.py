"""crud protein"""

from app import schemas
from app.crud.crud_base import CRUDBase
from app.models import Protein


class CRUDProtein(CRUDBase[Protein, schemas.ProteinCreate, schemas.ProteinUpdate]):
    def get_all(self, db) -> Protein:
        """Get all protein"""
        return db.query(Protein).all()
    
    def get_by_id(self, db, *, id: int) -> Protein:
        """Get protein by id"""
        return db.query(Protein).filter(Protein.id == id).first()
    
    def get_by_name(self, db, *, name: str) -> Protein:
        """Get agencia by name"""
        return db.query(Protein).filter(Protein.name == name).first()


protein = CRUDProtein(Protein)