"""Styles Cy models"""

from sqlalchemy import Column, Integer, JSON
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from app.db.base_class import BaseWithDatetime


class Style(BaseWithDatetime):
    @declared_attr
    def __tablename__(cls) -> str:
        return "style"

    TYPE_CHOICES = [
        (0, "Protein"),
        (1, "Edge"),
    ]

    id = Column(Integer, primary_key=True, index=True)
    ccs_styles = Column(JSON, nullable=True)
    cytoscape_styles = Column(JSON, nullable=True)
    type = Column(Integer, nullable=False, default=0)
    protein = relationship("Protein", back_populates="style")
    complex_protein = relationship("Complex", back_populates="style")
    edge = relationship("Edge", back_populates="style")
