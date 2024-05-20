from sqlalchemy import Column, String, Float, Boolean, Integer  # type: ignore
from sqlalchemy.ext.declarative import declared_attr  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore

from app.db.base_class import BaseWithDatetime


class Layout(BaseWithDatetime):
    @declared_attr
    def __tablename__(cls) -> str:
        return "layout"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    animated = Column(Boolean, nullable=False, default=False)
    node_spacing = Column(Float, nullable=False, default=0.0)
    randomize = Column(Boolean, nullable=False, default=False)
    max_simulation_time = Column(Integer, nullable=False, default=1000)
    graph = relationship("AbstractGraph", back_populates="layout")
