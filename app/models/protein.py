"""Protein models"""

from sqlalchemy import Column, String, Text, Float, Boolean, Integer, ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from app.db.base_class import BaseWithDatetime
from app.models.graph import ClusterGraph


class Protein(BaseWithDatetime):
    @declared_attr
    def __tablename__(cls) -> str:
        return "protein"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    url_info = Column(String(255), nullable=True)
    uniprotkb_id = Column(String(100), nullable=True)


class OverlappingProtein(BaseWithDatetime):
    @declared_attr
    def __tablename__(cls) -> str:
        return "overlapping_protein"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    url_info = Column(String(255), nullable=True)
    score = Column(Float, nullable=False)
    is_important = Column(Boolean, nullable=False, default=False)
    notes = Column(Text, nullable=True)
    cluster_graph_id = Column(Integer, ForeignKey("cluster_graph.id"), nullable=False)
    cluster_graph = relationship(
        ClusterGraph,
        back_populates="protein_complexes",
    )


class Proteome(BaseWithDatetime):
    @declared_attr
    def __tablename__(cls) -> str:
        return "proteome"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    url_info = Column(String(255), nullable=True)
    fasta_file_path = Column(String(255), nullable=True)
    uniprot_proteome_id = Column(String(255), nullable=True)
    ppi_graph = relationship("PPIGraph", back_populates="proteome")
