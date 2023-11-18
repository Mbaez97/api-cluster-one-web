"""Get Enrichment data"""
import math
from fastapi import (  # noqa F401 # type: ignore
    APIRouter,
    Depends,
    HTTPException,
)  # noqa F401 # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from app import crud
from app.api import deps


router = APIRouter()


def parse_enrichments(db, enrichments: list):
    _enrichment_parse = []
    for enrichment in enrichments:
        _go_term = crud.go_terms.get_by_id(db, id=enrichment.go_terms_id)  # type: ignore # noqa
        if enrichment.p_value < 0.05:  # Only show significant results
            _enrichment_parse.append(
                {
                    "id": enrichment.id,
                    "p_value": enrichment.p_value,
                    "bar_charge": -1 * math.log(enrichment.p_value),
                    "notes": enrichment.notes,
                    "go_term": {
                        "go_id": _go_term.go_id + " || " + _go_term.term,
                        # "go_id": _go_term.go_id,
                        "term": _go_term.term,
                        "description": _go_term.description,
                        "url_info": _go_term.url_info,
                        "domain_str": _go_term.DOMINIO_CHOICES[_go_term.domain],  # noqa
                        "domain": _go_term.domain,
                    },
                    "cluster_graph_id": enrichment.cluster_graph_id,
                }
            )
    return _enrichment_parse


# GET
@router.get("/complex/{cluster_id}/")
def get_by_complex(
    cluster_id: int,
    db: Session = Depends(deps.get_db),
):
    """
    Get by complex
    """
    enrichments = crud.enrichment.get_by_cluster_id(db, cluster_id=cluster_id)
    if not enrichments:
        raise HTTPException(status_code=404, detail="Enrichment not found")
    return parse_enrichments(db, enrichments)


@router.get("/params/")
def get_params_scores(
    db: Session = Depends(deps.get_db),
    param_id: int = 1,
):
    """
    Get params scores
    """
    params = crud.params.get_by_id(db, id=param_id)
    if not params:
        raise HTTPException(status_code=404, detail="Params not found")
    _response = {
        "id": 3,
        "ora_bp_score": round(params.ora_bp_score, 2)
        if params.ora_bp_score
        else 0,  # noqa
        "ora_mf_score": round(params.ora_mf_score, 2)
        if params.ora_mf_score
        else 0,  # noqa
        "ora_cc_score": round(params.ora_cc_score, 2)
        if params.ora_cc_score
        else 0,  # noqa
        "ppi_graph_id": round(params.ppi_graph_id, 2)
        if params.ppi_graph_id
        else 0,  # noqa
    }
    return _response
