"""Get Enrichment data"""
from fastapi import (  # noqa F401 # type: ignore
    APIRouter,
    Depends,
    HTTPException,
)  # noqa F401 # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from app import crud
from app.api import deps


router = APIRouter()


# GET
@router.get("/complex/{cluster_id}/")
def get_by_complex(
    cluster_id: int,
    db: Session = Depends(deps.get_db),
):
    """
    Get by complex
    """
    enrichment = crud.enrichment.get_by_cluster_id(db, cluster_id=cluster_id)
    if not enrichment:
        raise HTTPException(status_code=404, detail="Enrichment not found")
    return enrichment
