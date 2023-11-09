"""agencia schema"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class ProteinBase(BaseModel):
    id: Optional[int]
    name: Optional[str]
    description: Optional[str]
    url_info: Optional[str]
    # score: Optional[float]


class ProteinUpdate(ProteinBase):
    updated_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class ProteinCreate(ProteinBase):
    created_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updated_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class ProteinResponse(BaseModel):
    proteins: List[ProteinBase]


class OverlappingProteinBase(BaseModel):
    id: Optional[int]
    name: Optional[str]
    description: Optional[str]
    url_info: Optional[str]
    # score: Optional[float]
    is_important: Optional[bool]
    notes: Optional[str]
    cluster_graph_id: Optional[int]


class OverlappingProteinUpdate(OverlappingProteinBase):
    updated_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class OverlappingProteinCreate(OverlappingProteinBase):
    created_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updated_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
