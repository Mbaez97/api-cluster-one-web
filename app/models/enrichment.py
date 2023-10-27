"""Protein models"""

from sqlalchemy import Column, String, Text, Float, Boolean, Integer, ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from app.db.base_class import BaseWithDatetime
from app.models.graph import ClusterGraph


class GoTerms(BaseWithDatetime):
    @declared_attr
    def __tablename__(cls) -> str:
        return "go_terms"

    DOMINIO_CHOICES = (
        ("BP", "Biological Process"),
        ("CC", "Cellular Component"),
        ("MF", "Molecular Function"),
    )

    id = Column(Integer, primary_key=True, index=True)
    term = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    url_info = Column(String(255), nullable=True)
    domain = Column(String(2), nullable=False)
    enrichment = relationship(
        "Enrichment",
        back_populates="go_terms",
    )


class Enrichment(BaseWithDatetime):
    @declared_attr
    def __tablename__(cls) -> str:
        return "enrichment"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    p_value = Column(Float, nullable=False)
    is_important = Column(Boolean, nullable=False, default=False)
    notes = Column(Text, nullable=True)
    go_terms_id = Column(Integer, ForeignKey("go_terms.id"), nullable=False)
    go_terms = relationship(
        GoTerms,
        back_populates="enrichment",
    )
    cluster_graph_id = Column(Integer, ForeignKey("cluster_graph.id"), nullable=False)
    cluster_graph = relationship(
        ClusterGraph,
        back_populates="enrichment",
    )
