from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user, require_roles

router = APIRouter(prefix="/reports", tags=["reports"])

# ---------------- REPORTES (padre) ----------------
@router.get("/{nombre_entidad}")
@router.get("/{nombre_entidad}/")
def get_reportes_por_entidad(
    nombre_entidad: str,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    # Buscar todos los registros para esa entidad (case-insensitive)
    registros = (
        db.query(models.Reporte)
        .filter(models.Reporte.entidad.ilike(nombre_entidad))
        .all()
    )

    if not registros:
        raise HTTPException(status_code=404, detail="No records found for that entity")

    # Convertirlos al formato requerido
    resultado = {
        "entidad": registros[0].entidad,
        "indicadores": [
            {"indicador": r.indicador, "accion": r.accion}
            for r in registros
            if r.indicador is not None and r.accion is not None
        ],
    }
    return resultado

@router.post("")
@router.post("/")
def cargar_reportes(
    payload: schemas.ReporteEntradaLista,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    nuevos = []

    for r in payload.reportes:
        nuevo = models.Reporte(
            entidad=r.entidad,
            indicador=r.indicador,
            accion=r.accion
        )
        db.add(nuevo)
        nuevos.append(nuevo)

    db.commit()
    return {"insertados": len(nuevos)}


@router.delete("/")
def borrar_todos_los_reportes(
    db: Session = Depends(get_db),
    user: models.User = Depends(require_roles(["admin"])),
):
    num_borrados = db.query(models.Reporte).delete()
    db.commit()
    return {"borrados": num_borrados}