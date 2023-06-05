"""crud protein"""

from app import schemas
from app.crud.crud_base import CRUDBase
from app.models import Protein, Style
from app.api.utils import get_random_color, get_complex_protein_color, generate_random_styles



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
    
    def quick_creation(self, db, *, name: str) -> Protein:
        _data = name
        _url = 'www.ebi.ac.uk/proteins/api/proteins/'
        _style = generate_random_styles()
        _style_objet = Style(
            ccs_styles=_style,
            type=0,
        )
        db.add(_style_objet)

        protein_1 = Protein(
            name=_data,
            description="Automatic node created from PPI file",
            score=0.0,
            url_info=_url + _data,
            style=_style_objet
        )
        db.add(protein_1)
        db.commit()
        print("Protein created: ", protein_1.name)
        return protein_1


protein = CRUDProtein(Protein)