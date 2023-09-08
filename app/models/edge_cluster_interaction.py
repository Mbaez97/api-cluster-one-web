" EdgePPIInteraction Model "
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Column, Integer, ForeignKey, Float

from app.db.base_class import BaseWithDatetime


class EdgeClusterInteraction(BaseWithDatetime):
    @declared_attr
    def __tablename__(cls) -> str:
        return "edge_cluster_interaction"

    id = Column(Integer, primary_key=True, index=True)
    weight = Column(Float, nullable=False)
    edge_id = Column(Integer, ForeignKey("edge.id"))
    cluster_graph_id = Column(Integer, ForeignKey("cluster_graph.id"))
