"""Edge models"""

from sqlalchemy import Column, Float, Boolean, Integer, ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from app.db.base_class import BaseWithDatetime
from app.models.protein import Protein


class Edge(BaseWithDatetime):
    @declared_attr
    def __tablename__(cls) -> str:
        return "edge"

    DIRECTION_CHOICES = [
        (0, "None"),
        (1, "A to B"),
        (2, "B to A"),
        (3, "Both"),
    ]

    id = Column(Integer, primary_key=True, index=True)
    protein_a_id = Column(Integer, ForeignKey("protein.id"), nullable=True)
    protein_b_id = Column(Integer, ForeignKey("protein.id"), nullable=True)
    protein_a = relationship(Protein, foreign_keys=[protein_a_id])
    protein_b = relationship(Protein, foreign_keys=[protein_b_id])
    weight = Column(Float, nullable=False)
    has_direction = Column(Boolean, nullable=False, default=False)
    direction = Column(Integer, nullable=False, default=0)
    ppi_interactions = relationship(
        "PPIGraph", secondary="edge_ppi_interaction", back_populates="edge"
    )
    cluster_interactions = relationship(
        "ClusterGraph", secondary="edge_cluster_interaction", back_populates="edges"
    )
