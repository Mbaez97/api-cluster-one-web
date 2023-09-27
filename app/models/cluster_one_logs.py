"""Edge models"""

from sqlalchemy import Column, Float, Boolean, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from app.db.base_class import BaseWithDatetime


class ClusterOneLogParams(BaseWithDatetime):
    @declared_attr
    def __tablename__(cls) -> str:
        return "cluster_one_log_params"

    @declared_attr
    def __table_args__(cls):
        return (UniqueConstraint("min_size", "min_density", "max_overlap", "penalty", "ppi_graph_id"),)

    id = Column(Integer, primary_key=True, index=True)
    min_size = Column(Integer, nullable=True, default=0)
    min_density = Column(Float, nullable=True, default=0.0)
    max_overlap = Column(Float, nullable=True, default=0.0)
    penalty = Column(Float, nullable=True, default=0.0)
    ppi_graph_id = Column(Integer, ForeignKey("ppi_graph.id"), nullable=False)
    ppi_graph = relationship("PPIGraph", back_populates="cluster_one_log_params")

