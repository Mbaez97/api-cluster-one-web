" ComplexCL1Interaction Model "
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Column, Integer, ForeignKey

from app.db.base_class import BaseWithDatetime


class ComplexClusterOneIteraction(BaseWithDatetime):
    @declared_attr
    def __tablename__(cls) -> str:
        return "complex_cluster_one_interaction"

    id = Column(Integer, primary_key=True, index=True)
    cluster_id = Column(Integer, ForeignKey("cluster_graph.id"))
    complex_id = Column(Integer, ForeignKey("protein_complex.id"))
