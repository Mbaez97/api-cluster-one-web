"""agencia schema"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class ParamsBase(BaseModel):
    id: Optional[int]
    min_size: Optional[int]
    min_density: Optional[float]
    max_overlap: Optional[float]
    penalty: Optional[float]


class ParamsUpdate(ParamsBase):
    updated_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class ParamsCreate(ParamsBase):
    created_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updated_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class ParamsResponse(BaseModel):
    proteins: List[ParamsBase]
