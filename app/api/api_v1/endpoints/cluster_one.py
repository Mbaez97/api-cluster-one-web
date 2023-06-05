"""Assigns Raspadita box, libro and cartones"""
from datetime import datetime
from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.orm import Session

# from app import crud
from app.api import deps
# from app.models import CartonCorredor, Libro, Umn, Usuario
# from app.models.user import UsuarioUmn
# from app.schemas.box import BoxAssign
# from app.schemas.carton import CartonAssign
# from app.schemas.libro import LibroAssign
# from app.utils import (
#     get_libro_code_from_boleta,
#     has_permission,
#     normalize_carton_codigo,
# )

router = APIRouter()


# # Assigns
# @router.post("/umns/{umn_id}/boxes", response_model=BoxAssign)
# def assign_box(
#     umn_id: int,
#     db: Session = Depends(deps.get_db),
#     body: BoxAssign = Body(...),
#     current_user: Usuario = Depends(deps.get_current_active_user),
# ):
#     """
#     Assign a boxes to an umn
#     """
#     try:
#         if not has_permission(
#             db=db,
#             current_user=current_user,
#             roles_allowed=["admin_juego", "raspa_operativa", "tdp_operativa"],
#         ):
#             raise HTTPException(
#                 status_code=403, detail="No tienes permiso para realizar esta acción"
#             )
#         umn = db.query(Umn).filter(Umn.id == umn_id).first()
#         for code in body.code_list:
#             box = crud.box.get_by_code(db, code=code)
#             if not box:
#                 raise HTTPException(status_code=404, detail="Box not found")

#             if box.estado in ["recibido", "compartido", "notificado"]:
#                 raise HTTPException(
#                     status_code=400,
#                     detail=f"La caja: {box.codigo} se encuentra {box.estado}",
#                 )

#             box = crud.box.update(
#                 db,
#                 obj_in={"estado": "notificado", "fecha_asignacion": datetime.now()},
#                 db_obj=box,
#                 commit=False,
#             )
#             libros = crud.libro.assign_libros_from_box(
#                 db, umn=umn, box_id=box.id, commit=False
#             )
#             if not box.alta:
#                 crud.carton.create_cartones_from_libros(
#                     db, libros=libros, commit=False,
#                 )
#                 box.alta = True
#         db.commit()
#     except HTTPException as exc:
#         db.rollback()
#         raise exc
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=400, detail=str(e))
#     return body



# # UnAssigns
# @router.delete("/corredores/{corredor_id}/cartones", response_model=CartonAssign)
# def unassign_carton_corredor(
#     corredor_id: int,
#     db: Session = Depends(deps.get_db),
#     body: CartonAssign = Body(...),
#     stock: bool = Query(True),
#     current_user: Usuario = Depends(deps.get_current_active_user),
# ):  # Validar que la umn del corredor sea la misma que la umn del libro asignado.
#     """
#         UnAssign carton-boletas to corredor
#     """

#     try:
#         if not has_permission(
#             db=db,
#             current_user=current_user,
#             roles_allowed=[
#                 "admin_juego",
#                 "raspa_gerencia",
#                 "agencia",
#                 "tdp_operativa",
#                 "umn",
#             ],
#         ):
#             raise HTTPException(
#                 status_code=403, detail="No tienes permiso para realizar esta acción"
#             )
#         corredor = crud.corredor.get(db, id=corredor_id)
#         for code_raw in body.code_list:
#             code = normalize_carton_codigo(code_raw)
#             carton: Any = crud.carton.get_by_code(db, code=code)
#             if not corredor:
#                 raise HTTPException(status_code=404, detail="Corredor not Found")
#             if not carton:
#                 raise HTTPException(status_code=404, detail="Boleta not Found")
#             # Check if the umn of corredor_id is the same as the assigned libro to UMN
#             if carton.corredor_id != corredor_id:
#                 raise HTTPException(
#                     status_code=400, detail="Boleta no corresponde al corredor"
#                 )
#             if carton.estado != "asignado":
#                 raise HTTPException(
#                     status_code=400, detail="Boleta no se encuentra asignada"
#                 )
#             if carton.prorroga:
#                 raise HTTPException(
#                     status_code=400,
#                     detail="Esta boleta no se puede desasignar. Ya fue prorrogada",
#                 )
#             if carton.libro.umn.id == corredor.umn.id and carton.estado == "asignado":
#                 obj_in = {"fecha_asignacion": datetime.now(), "prorroga": True}

#                 crud.carton.update(
#                     db, db_obj=carton, obj_in=obj_in, commit=False,
#                 )
#                 carton.libro.asignados -= 1
#                 carton.belonged_to_corredores.append(
#                     CartonCorredor(
#                         corredor_id=corredor_id,
#                         updated_at=datetime.now(),
#                         detalle="carton prorrogado",
#                     )
#                 )

#                 if carton.libro.asignados == 0:
#                     estado_libro = "recibido"
#                 else:
#                     estado_libro = "compartido"

#                 crud.libro.update(
#                     db,
#                     db_obj=carton.libro,
#                     obj_in={"estado": estado_libro},
#                     commit=False,
#                 )
#             else:
#                 raise HTTPException(status_code=400, detail="Boleta no corresponde Umn")
#         db.commit()
#     except HTTPException as exc:
#         db.rollback()
#         raise exc
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=400, detail=str(e))
#     return body



# Reception
# @router.put("/umns/{umn_id}/boxes", response_model=BoxAssign)
# def reception_box_by_umn(
#     umn_id: int,
#     db: Session = Depends(deps.get_db),
#     body: BoxAssign = Body(...),
#     current_user: Usuario = Depends(deps.get_current_active_user),
# ):
#     """
#         Confirm reception boxes by umn
#     """
#     try:
#         if not has_permission(
#             db=db,
#             current_user=current_user,
#             roles_allowed=[
#                 "admin_juego",
#                 "raspa_gerencia",
#                 "agencia",
#                 "tdp_operativa",
#                 "umn",
#             ],
#         ):
#             raise HTTPException(
#                 status_code=403, detail="No tienes permiso para realizar esta acción"
#             )
#         # Hay que hacer las comprobaciones con la umn
#         for code in body.code_list:
#             box = crud.box.get_by_code(db, code=code)

#             if not box:
#                 raise HTTPException(status_code=404, detail="Box not found")
#             if box.estado == "recibido":
#                 raise HTTPException(status_code=400, detail="Box already received")
#             libros: List[Libro] = box.libro  # type: ignore
#             umns: List[UsuarioUmn] = current_user.usuario_umn  # type: ignore
#             if umns[0].umn.agencia_numero == libros[
#                 0
#             ].umn.agencia_numero or has_permission(
#                 db=db, current_user=current_user, roles_allowed=["admin_juego"]
#             ):  # for review
#                 crud.box.update(
#                     db, db_obj=box, obj_in={"estado": "recibido"}, commit=False
#                 )
#             else:
#                 raise HTTPException(
#                     status_code=400, detail="La caja no correspode a tu Agencia"
#                 )
#             for libro in box.libro:  # type: ignore
#                 if libro.umn.agencia.metropolitano:
#                     crud.libro.update(
#                         db,
#                         db_obj=libro,
#                         obj_in={
#                             "estado": "recibido",
#                             "estado_inventario": "stock",
#                             "registro_inventario": datetime.now(),
#                         },
#                         commit=False,
#                     )
#                     crud.libro.create_history(
#                         db, umn_id=umn_id, details="recibido", libro=libro, commit=False
#                     )
#                 else:
#                     crud.libro.update(
#                         db,
#                         db_obj=libro,
#                         obj_in={
#                             "estado_inventario": "stock",
#                             "registro_inventario": datetime.now(),
#                         },
#                         commit=False,
#                     )
#                     crud.libro.create_history(
#                         db, umn_id=umn_id, details="stock", libro=libro, commit=False
#                     )
#         db.commit()
#     except HTTPException as exc:
#         raise exc
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=400, detail=str(e))
#     return body

