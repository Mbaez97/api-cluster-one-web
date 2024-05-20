"""Get Graph data"""

import os
import json
from fastapi import (  # type: ignore
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
from app.taskapp.celery import async_insert_redis
from redis import Redis  # type: ignore
from libs.lib_manejo_csv import detect_file_type, lee_csv, lee_txt, parse_ppi_csv_to_txt

router = APIRouter()


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
    r.close()
    return {"weight": _weight}


def get_weight_by_interactions_list(
    interactions_key: list,
):
    """
    Get weight by protein
    """
    r = Redis(host="redis", port=6379, db=3)
    data = r.mget(interactions_key)
    if not data:
        return None
    r.close()
    return data


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
        _type = detect_file_type(file.filename)
        _file_path = f"/app/app/media/ppi/{file.filename}"
        print(_file_path)
        with open(_file_path, "wb") as buffer:
            buffer.write(file.file.read())
            buffer.close()
        if _type == "txt":
            _file = lee_txt(_file_path)
            _size = len(_file)
            _file_name = file.filename
        elif _type == "csv":
            _old_file_path = _file_path
            _file = lee_csv(_old_file_path)
            _data_columns = len(_file[0])
            _file_path = _file_path.replace(".csv", ".txt")
            if _data_columns < 3:
                weight = False
            else:
                weight = True
            parse_ppi_csv_to_txt(_old_file_path, _file_path, wieght=weight)
            # Delete old file
            os.remove(_old_file_path)
            _size = len(lee_txt(_file_path))
            _file_name = file.filename.replace(".csv", ".txt")
        else:
            raise HTTPException(
                status_code=404, detail="File type not supported"
            )  # noqa
        _layout = db.query(Layout).filter(Layout.name == "random").first()
        if not _layout:
            obj = {
                "name": "random",
                "animated": False,
                "node_spacing": 10,
                "randomize": True,
                "max_simulation_time": 1000,
            }
            _layout = crud.layout.quick_create_layout(db, obj=obj)
        _data = {
            "external_weight": 0,
            "internal_weight": 0,
            "density": 0,
            "size": _size,
            "quality": 0,
            "layout": _layout,
            "data": _file_path,
            "name": file.filename,
            "preloaded": False,
        }
        _ppi_obj = crud.ppi_graph.get_ppi_by_name(db, name=_file_name)
        if not _ppi_obj:
            print("LOGS: PPI will be created")
            _new_ppi = crud.ppi_graph.create_ppi_from_file(db, obj=_data)
            # Async insert edges to redis
            async_insert_redis.delay(_new_ppi.id)
            response = {
                "id": _new_ppi.id,
                "name": _new_ppi.name,
                "data": _new_ppi.data,
                "density": _new_ppi.density,
                "size": _new_ppi.size,
                "preloaded": _new_ppi.preloaded,
            }
            return response
        print("LOGS: PPI already exists")
        # Async insert edges to redis
        async_insert_redis.delay(_ppi_obj.id)
        response = {
            "id": _ppi_obj.id,
            "name": _ppi_obj.name,
            "data": _ppi_obj.data,
            "density": _ppi_obj.density,
            "size": _ppi_obj.size,
            "preloaded": _ppi_obj.preloaded,
        }
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
    return {"status": "ok", "size": _ppi_obj.size}


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
