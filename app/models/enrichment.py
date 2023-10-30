"""Enrichment models"""

from sqlalchemy import Column, String, Text, Float, Integer, ForeignKey  # type: ignore # noqa
from sqlalchemy.ext.declarative import declared_attr  # type: ignore # noqa
from sqlalchemy.orm import relationship  # type: ignore # noqa

from app.db.base_class import BaseWithDatetime


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

    STATE_CHOICES = {
        "pending": 1,
        "running": 2,
        "completed": 3,
        "failed": 4,
    }

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    p_value = Column(Float, nullable=False)
    notes = Column(Text, nullable=True)
    state = Column(Integer, nullable=False, default=1)
    go_terms_id = Column(Integer, ForeignKey("go_terms.id"), nullable=False)
    go_terms = relationship(
        GoTerms,
        back_populates="enrichment",
    )
    cluster_graph_id = Column(Integer, ForeignKey("cluster_graph.id"), nullable=False)  # type: ignore # noqa
    # cluster_graph = relationship(
    #     "ClusterGraph",
    #     back_populates="enrichment",
    #     remote_side=[cluster_graph_id],
    #     foreign_keys=[cluster_graph_id],
    # )
