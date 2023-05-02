" EdgePPIInteraction Model "
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Column, Integer, ForeignKey

from src.db.base_class import BaseWithDatetime


class EdgeClusterInteraction(BaseWithDatetime):
    @declared_attr
    def __tablename__(cls) -> str:
        return "edge_cluster_interaction"

    id = Column(Integer, primary_key=True, index=True)
    edge_id = Column(Integer, ForeignKey("edge.id"))
    ppi_interaction_id = Column(Integer, ForeignKey("ppi_graph.id"))
