from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EdgeBase(BaseModel):
    id: Optional[int]
    protein_a_id: Optional[int]
    protein_b_id: Optional[float]
    weight: Optional[float]
    has_direction: Optional[bool]
    direction: Optional[int]


class EdgeUpdate(EdgeBase):
    updated_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class EdgeCreate(EdgeBase):
    created_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updated_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
