from app import schemas
from app.crud.crud_base import CRUDBase
from app.models import Enrichment

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


enrichment = CRUDEnrichment(Enrichment)
