"""Graphs models"""

from sqlalchemy import Column, String, Float, Boolean, Integer
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

# Models
from src.db.base_class import BaseWithDatetime
from src.models.edge import Edge


class AbstractGraph(BaseWithDatetime):
    @declared_attr
    def __tablename__(cls) -> str:
        return "graph"

    id = Column(Integer, primary_key=True, index=True)
    size = Column(Integer, nullable=False)
    density = Column(Float, nullable=False)
    # layout_id = Column(Integer, ForeignKey("layout.id"), nullable=False)


class PPIGraph(AbstractGraph):
    @declared_attr
    def __tablename__(cls) -> str:
        return "ppi_graph"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    preloaded = Column(Boolean, nullable=False, default=False)
    # Definición de la relación muchos a muchos con la tabla "edges"
    edges = relationship(
        Edge,
        secondary="edge_ppi_interaction",
        back_populates="ppi_interactions"
    )


class ClusterGraph(AbstractGraph):
    @declared_attr
    def __tablename__(cls) -> str:
        return "cluster_graph"

    id = Column(Integer, primary_key=True, index=True)
    quality = Column(Float, nullable=False)
    external_weight = Column(Float, nullable=False)
    internal_weight = Column(Float, nullable=False)
    # Definición de la relación muchos a muchos con la tabla "edges"
    edges = relationship(
        Edge,
        secondary="edge_cluster_interaction",
        back_populates="cluster_interactions"
    )
