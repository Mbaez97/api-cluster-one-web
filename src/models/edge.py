"""Edge models"""

from sqlalchemy import Column, String, Text, Float, Boolean, Integer, ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from src.db.base_class import BaseWithDatetime
from src.models.protein import Protein
from src.models.style import Style


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

    protein_a_id = Column(Integer, ForeignKey("Protein.id"), nullable=False)
    protein_b_id = Column(Integer, ForeignKey("Protein.id"), nullable=False)
    protein_a = relationship(Protein, foreign_keys=[protein_a_id])
    protein_b = relationship(Protein, foreign_keys=[protein_b_id])
    weight = Column(Float, nullable=False)
    has_direction = Column(Boolean, nullable=False, default=False)
    direction = Column(Integer, nullable=False, default=0)
    style_id = Column(Integer, ForeignKey("style.id"), nullable=False)
    style = relationship(Style, back_populates="edge")