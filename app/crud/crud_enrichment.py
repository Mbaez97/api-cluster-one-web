from app import schemas
from app.crud.crud_base import CRUDBase
from app.models import Enrichment, GoTerms

"""crud enrichment"""


class CRUDEnrichment(CRUDBase[Enrichment, schemas.EnrichmentBase, schemas.EnrichmentUpdate]):  # type: ignore # noqa"
    def get_by_cluster_id(self, db, *, cluster_id: int) -> Enrichment:
        """Get by cluster id"""
        return (
            db.query(Enrichment)
            .filter(Enrichment.cluster_graph_id == cluster_id)
            .filter(Enrichment.state == 3)
            .first()
        )

    def quick_creation(self, db, *, obj: dict) -> Enrichment:
        """Quick creation"""
        db_obj = Enrichment(  # type: ignore
            p_value=obj["p_value"],
            notes=obj["notes"],
            state=obj["state"],
            go_terms_id=obj["go_terms_id"],
            cluster_graph_id=obj["cluster_graph_id"],
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDGoTerms(CRUDBase[GoTerms, schemas.GoTermsBase, schemas.GoTermsUpdate]):  # type: ignore # noqa"
    def get_by_term(self, db, *, term: str) -> GoTerms:
        """Get by term"""
        return db.query(GoTerms).filter(GoTerms.term == term).first()

    def get_by_go_id(self, db, *, go_id: str) -> GoTerms:
        """Get by go_id"""
        return db.query(GoTerms).filter(GoTerms.go_id == go_id).first()

    def quick_creation(self, db, *, obj: dict) -> GoTerms:
        """Quick creation"""
        db_obj = GoTerms(  # type: ignore
            term=obj["term"],
            description=obj["description"],
            url_info=obj["url_info"],
            domain=obj["domain"],
            go_id=obj["go_id"],
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


enrichment = CRUDEnrichment(Enrichment)
go_terms = CRUDGoTerms(GoTerms)
