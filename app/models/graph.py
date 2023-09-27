"""Graphs models"""

from sqlalchemy import Column, String, Float, Boolean, Integer, ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

# Models
from app.db.base_class import BaseWithDatetime
from app.models.layout import Layout


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

    id = Column(Integer, ForeignKey("graph.id"), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    preloaded = Column(Boolean, nullable=False, default=False)
    data = Column(String(255), nullable=True)
    # Definición de la relación muchos a muchos con la tabla "edges"
    edge = relationship(
        "Edge", secondary="edge_ppi_interaction", back_populates="ppi_interactions"
    )


class ClusterGraph(AbstractGraph):
    """
    ClusterGraph model
    I think this model represent all clusters detected by ClusterOne Algorithm.
    This is the complex man.
    """

    @declared_attr
    def __tablename__(cls) -> str:
        return "cluster_graph"

    id = Column(Integer, ForeignKey("graph.id"), primary_key=True, index=True)
    quality = Column(Float, nullable=False, default=0.0)
    external_weight = Column(Float, nullable=False, default=0.0)
    internal_weight = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.0)
    data = Column(String(255), nullable=True)
    is_complex = Column(Boolean, nullable=True, default=False)
    cluster_one_log_params_id = Column(
        Integer, ForeignKey("cluster_one_log_params.id"), nullable=True
    )
    # Definición de la relación muchos a muchos con la tabla "edges"
    edges = relationship(
        "Edge",
        secondary="edge_cluster_interaction",
        back_populates="cluster_interactions",
    )
    protein_complexes = relationship(
        "OverlappingProtein",
        back_populates="cluster_graph",
    )
    cluster_one_log_params = relationship(
        "ClusterOneLogParams",
        back_populates="cluster_graph",
    )
