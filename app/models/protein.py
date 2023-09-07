"""Protein models"""

from sqlalchemy import Column, String, Text, Float, Boolean, Integer
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from app.db.base_class import BaseWithDatetime


class Protein(BaseWithDatetime):
    @declared_attr
    def __tablename__(cls) -> str:
        return "protein"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    url_info = Column(String(255), nullable=True)
    score = Column(Float, nullable=False)
    # go_terms = relationship("GoTerm", back_populates="protein")


class Complex(BaseWithDatetime):
    @declared_attr
    def __tablename__(cls) -> str:
        return "protein_complex"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    url_info = Column(String(255), nullable=True)
    score = Column(Float, nullable=False)
    # go_terms = relationship("GoTerm", back_populates="protein")
    is_important = Column(Boolean, nullable=False, default=False)
    notes = Column(Text, nullable=True)
    cluster_graphs = relationship(
        "ClusterGraph",
        secondary="complex_cluster_one_interaction",
        back_populates="protein_complexes",
    )
