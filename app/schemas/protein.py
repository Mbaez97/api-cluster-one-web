"""agencia schema"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class ProteinBase(BaseModel):
    name: Optional[str]
    description: Optional[str]
    url_info: Optional[str]
    score: Optional[float]
    style_id: Optional[int]


class ProteinUpdate(ProteinBase):
    updated_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class ProteinCreate(ProteinBase):
    created_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updated_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class ProteinResponse(BaseModel):
    proteins: List[ProteinBase]
