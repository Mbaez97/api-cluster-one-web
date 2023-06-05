"""Graphs models"""

from sqlalchemy import Column, String, Float, Boolean, Integer, ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

# Models
from app.db.base_class import BaseWithDatetime
from app.models.edge import Edge
from app.models.layout import Layout
from app.models.protein import Complex


class AbstractGraph(BaseWithDatetime):
    @declared_attr
    def __tablename__(cls) -> str:
        return "graph"

    id = Column(Integer, primary_key=True, index=True)
    size = Column(Integer, nullable=False)
    density = Column(Float, nullable=False)
    layout_id = Column(Integer, ForeignKey("layout.id"), nullable=False)
    layout = relationship(Layout, back_populates="graph")


class PPIGraph(AbstractGraph):
    @declared_attr
    def __tablename__(cls) -> str:
        return "ppi_graph"

    id = Column(Integer, ForeignKey('graph.id') , primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    preloaded = Column(Boolean, nullable=False, default=False)
    data = Column(String(255), nullable=True)
    # Definición de la relación muchos a muchos con la tabla "edges"
    edge = relationship(
        Edge, secondary="edge_ppi_interaction", back_populates="ppi_interactions"
    )


class ClusterGraph(AbstractGraph):
    @declared_attr
    def __tablename__(cls) -> str:
        return "cluster_graph"

    id = Column(Integer, ForeignKey('graph.id') , primary_key=True, index=True)
    quality = Column(Float, nullable=False)
    external_weight = Column(Float, nullable=False)
    internal_weight = Column(Float, nullable=False)
    # Definición de la relación muchos a muchos con la tabla "edges"
    edges = relationship(
        Edge,
        secondary="edge_cluster_interaction",
        back_populates="cluster_interactions",
    )
    protein_complexes = relationship(
        Complex, 
        secondary="complex_cluster_one_interaction",
        back_populates="cluster_graphs"
    )
