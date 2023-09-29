"""Get Graph data"""
import json
from fastapi import (  # noqa F401 # type: ignore
    APIRouter,
    Depends,
    HTTPException,
    File,
    UploadFile,
)  # noqa F401 # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from app import crud
from app.api import deps
from app.models import Layout
from app.taskapp.celery import async_creation_edge_for_ppi, async_insert_redis
from redis import Redis  # type: ignore

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
            async_insert_redis.delay(_new_ppi.id)
            async_creation_edge_for_ppi.delay(_new_ppi.id)
            response = {
                "id": _new_ppi.id,
                "name": _new_ppi.name,
                "data": _new_ppi.data,
                "density": _new_ppi.density,
                "size": _new_ppi.size,
                "preloaded": _new_ppi.preloaded,
            }
            return response
        async_insert_redis.delay(_ppi_obj.id)
        async_creation_edge_for_ppi.delay(_ppi_obj.id)
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


@router.post("/ppi/preloaded/update/")
def update_redis_preloaded(
    db: Session = Depends(deps.get_db),
    file_name: str = "",
):
    """
    Create PPI data from file
    """
    _ppi_obj = crud.ppi_graph.get_ppi_by_name(db, name=file_name)
    if not _ppi_obj:
        raise HTTPException(status_code=404, detail="PPI not found")
    async_insert_redis.delay(_ppi_obj.id)
    print("LOGS: PPI updated")
    return {"status": "ok"}


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
    for ppi in _ppi:  # type: ignore
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
                "file_name": ppi.name,
            }
        )
    return response


@router.get("/ppi/proteins/")
def get_weight_by_protein(
    ppi_id: int,
    protein1_id: int,
    protein2_id: int,
):
    """
    Get weight by protein
    """
    r = Redis(host="redis", port=6379, db=3)
    _key = f"{protein1_id}-{protein2_id}-{ppi_id}"
    data = r.get(_key)
    if not data:
        return {"weight": -1}
    _data = json.loads(data.decode("utf-8"))
    _weight = _data["weight"]
    return {"weight": _weight}
