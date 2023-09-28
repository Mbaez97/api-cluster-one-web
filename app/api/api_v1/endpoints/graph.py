"""Get Graph data"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.models import Layout

router = APIRouter()


# POST
@router.post("/ppi/")
def get_or_create_ppi_graph_from_file(
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
        _ppi_obj = crud.ppi_graph.get_ppi_by_name(db, name=file.filename)
        if not _ppi_obj:
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
        response = {
            "id": _ppi_obj.id,
            "name": _ppi_obj.name,
            "data": _ppi_obj.data,
            "density": _ppi_obj.density,
            "size": _ppi_obj.size,
            "preloaded": _ppi_obj.preloaded,
        }
        print("LOGS: PPI already exists")
        return response
    else:
        raise HTTPException(status_code=404, detail="File not found")


# GET
@router.get("/ppi/all/")
def get_all_ppi_graph(
    db: Session = Depends(deps.get_db),
):
    """
    Get All PPI data
    """
    _ppi = crud.ppi_graph.get_all_ppi(db)
    response = []
    for ppi in _ppi:
        response.append(
            {
                "id": ppi.id,
                "name": ppi.name.replace(".csv", "")
                .replace(".txt", "")
                .upper(),  # noqa
                "data": ppi.data,
                "density": ppi.density,
                "size": ppi.size,
                "preloaded": ppi.preloaded,
            }
        )
    return response
