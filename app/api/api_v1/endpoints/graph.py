"""Get Graph data"""
from datetime import datetime
from typing import Any, List

from fastapi.responses import ORJSONResponse
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.models import Layout

router = APIRouter()


# GET
# @router.get("/ppi/", response_model=ORJSONResponse)
# def get_ppi_graph(
#     db: Session = Depends(deps.get_db),
#     ppi_id: int = Query(None, description="PPI ID", gt=0),
# ):
#     """
#     Get All PPI data
#     """
#     graph = crud.ppi_graph.get_all_ppi(db)
#     if not graph:
#         raise HTTPException(status_code=404, detail="PPIs not found")
#     if ppi_id:
#         graph = crud.ppi_graph.get_ppi_by_id(db, id=ppi_id)
#         if not graph:
#             raise HTTPException(status_code=404, detail="PPI not found")
#     return graph


# @router.get("/cluster/", response_model=ORJSONResponse)
# def get_cluster_graph(
#     db: Session = Depends(deps.get_db),
#     cluster_id: int = Query(None, description="Cluster ID", gt=0),
# ):
#     """
#     Get All Cluster data
#     """
#     graph = crud.cluster_graph.get_all_cluster(db)
#     if not graph:
#         raise HTTPException(status_code=404, detail="Clusters not found")
#     if cluster_id:
#         graph = crud.cluster_graph.get_cluster_by_id(db, id=cluster_id)
#         if not graph:
#             raise HTTPException(status_code=404, detail="Cluster not found")
#     # breakpoint()
#     return graph


# POST
@router.post("/ppi/")
def create_ppi_graph_from_file(
    db: Session = Depends(deps.get_db),
    file: UploadFile = File(None),
):
    """
    Create PPI data from file
    """
    if file:
        # Save file in media
        _file_path = f"/app/app/media/ppi/{file.filename}"
        with open(_file_path, "wb") as buffer:
            buffer.write(file.file.read())
            buffer.close()
        _layout = db.query(Layout).filter(Layout.name == "random").first()
        _data = {
            "external_weight": 0,
            "internal_weight": 0,
            "density": 0,
            "size": 0,
            "quality": 0,
            "layout": _layout,
            "data": _file_path,
            "name": file.filename,
            "preloaded": False,
        }
        _new_ppi = crud.ppi_graph.create_ppi_from_file(db, obj=_data)
        response = {
            "id": _new_ppi.id,
            "name": _new_ppi.name,
            "data": _new_ppi.data,
            "density": _new_ppi.density,
            "size": _new_ppi.size,
            "preloaded": _new_ppi.preloaded,
        }
        return response
    else:
        raise HTTPException(status_code=404, detail="File not found")
