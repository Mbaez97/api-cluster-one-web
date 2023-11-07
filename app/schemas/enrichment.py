"""Enrichment schema"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class EnrichmentBase(BaseModel):
    id: Optional[int]
    name: Optional[str]
    p_value: Optional[float]
    notes: Optional[str]
    go_terms_id: Optional[int]


class EnrichmentUpdate(EnrichmentBase):
    updated_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class EnrichmentCreate(EnrichmentBase):
    created_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updated_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class GoTermsBase(BaseModel):
    id: Optional[int]
    term: Optional[str]
    description: Optional[str]
    url_info: Optional[str]
    domain: Optional[str]


class GoTermsUpdate(GoTermsBase):
    updated_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class GoTermsCreate(GoTermsBase):
    created_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updated_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
