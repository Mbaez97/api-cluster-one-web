"""Styles Cy models"""

from sqlalchemy import Column, Integer, JSON
from sqlalchemy.ext.declarative import declared_attr

from src.db.base_class import BaseWithDatetime


class Style(BaseWithDatetime):
    @declared_attr
    def __tablename__(cls) -> str:
        return "style"

    TYPE_CHOICES = [
        (0, "Protein"),
        (1, "Edge"),
    ]

    ccs_styles = Column(JSON, nullable=False)
    cytoscape_styles = Column(JSON, nullable=False)
    type = Column(Integer, nullable=False, default=0)
