"""Protein models"""

from sqlalchemy import Column, String, Text, Float, Boolean, Integer, ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from app.db.base_class import BaseWithDatetime
from app.models.style import Style


class Protein(BaseWithDatetime):
    @declared_attr
    def __tablename__(cls) -> str:
        return "protein"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    url_info = Column(String(255), nullable=True)
    score = Column(Float, nullable=False)
    style_id = Column(Integer, ForeignKey("style.id"), nullable=False)
    style = relationship(Style, back_populates="protein")
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
    style_id = Column(Integer, ForeignKey("style.id"), nullable=False)
    style = relationship(Style, back_populates="protein")
    # go_terms = relationship("GoTerm", back_populates="protein")
    is_important = Column(Boolean, nullable=False, default=False)
    notes = Column(Text, nullable=True)
