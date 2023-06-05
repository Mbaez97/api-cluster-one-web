"""agencia schema"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

class LayoutBase(BaseModel):
    id: Optional[int]
    name: Optional[str]
    animated: Optional[bool]
    node_spacing: Optional[float]
    max_simulation_time: Optional[int]

class GraphBase(BaseModel):
    id: Optional[int]
    size: Optional[int]
    density: Optional[float]
    score: Optional[float]
    style_id: Optional[int]
    layout_id: Optional[int]

class GraphUpdate(GraphBase):
    updated_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class GraphCreate(GraphBase):
    created_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updated_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class PPIGraphResponse(BaseModel):
    ppi: List[GraphBase]