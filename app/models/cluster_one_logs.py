"""Edge models"""

from sqlalchemy import Column, Float, Boolean, Integer, ForeignKey, UniqueConstraint  # type: ignore # noqa
from sqlalchemy.ext.declarative import declared_attr  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore

from app.db.base_class import BaseWithDatetime


class ClusterOneLogParams(BaseWithDatetime):
    @declared_attr
    def __tablename__(cls) -> str:
        return "cluster_one_log_params"

    @declared_attr
    def __table_args__(cls):
        return (
            UniqueConstraint(
                "min_size",
                "min_density",
                "max_overlap",
                "penalty",
                "ppi_graph_id",  # noqa
            ),
        )

    id = Column(Integer, primary_key=True, index=True)
    min_size = Column(Integer, nullable=True)
    min_density = Column(Float, nullable=True)
    max_overlap = Column(Float, nullable=True)
    penalty = Column(Float, nullable=True)
    ora_bp_score = Column(Float, nullable=True)
    ora_cc_score = Column(Float, nullable=True)
    ora_mf_score = Column(Float, nullable=True)
    ppi_graph_id = Column(Integer, ForeignKey("ppi_graph.id"), nullable=False)
    ppi_graph = relationship(
        "PPIGraph", back_populates="cluster_one_log_params"
    )  # noqa
    cluster_graph = relationship(
        "ClusterGraph", back_populates="cluster_one_log_params"
    )
