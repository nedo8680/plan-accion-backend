from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user, require_roles

router = APIRouter(prefix="/pqrds", tags=["pqrds"])

# ---------------- PQRDS (padre) ----------------
@router.get("")
@router.get("/")
def get_all_pqrds(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    pqrds = db.query(models.PQRD).all()
    return pqrds


@router.get("/count")
@router.get("/count/")
def count_pqrds(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    total = db.query(models.PQRD).count()
    return total


@router.get("/by/{label_pqrd}")
@router.get("/by/{label_pqrd}/")
def get_pqrd_by_label(
    label_pqrd: str,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    pqrd = db.query(models.PQRD).filter(models.PQRD.label == label_pqrd).first()

    if not pqrd:
        raise HTTPException(status_code=404, detail="PQRD not found")

    return pqrd


@router.get("/c1p1d1i01")
@router.get("/c1p1d1i01/")
def calcular_indicador_1(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    total_pqrds = db.query(models.PQRD).count()
    if total_pqrds == 0:
        return {"c1p1d1i01": 0.0}

    pqrds_a_tiempo = db.query(models.PQRD).filter(
        models.PQRD.fecha_vencimiento <= models.PQRD.fecha_radicado_salida
    ).count()

    indicador = (pqrds_a_tiempo / total_pqrds) * 100
    return {"c1p1d1i01": round(indicador, 2)}


@router.get("/c1p1d1i02")
@router.get("/c1p1d1i02/")
def calcular_indicador_2(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    total_pqrds = db.query(models.PQRD).count()
    if total_pqrds == 0:
        return {"c1p1d1i02": 0.0}

    pqrds_con_traslado = db.query(models.PQRD).filter(
        models.PQRD.dias_gestion < 5
    ).count()

    indicador = (pqrds_con_traslado / total_pqrds) * 100
    return {"c1p1d1i02": round(indicador, 2)}


@router.post("")
@router.post("/")
def cargar_pqrds(
    payload: schemas.PqrdEntradaLista,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    nuevos = []

    for p in payload.pqrds:
        nuevo = models.PQRD(
            label=p.label,
            fecha_vencimiento=p.fecha_vencimiento if p.fecha_vencimiento != "" else None,
            fecha_radicado_salida=p.fecha_radicado_salida if p.fecha_radicado_salida != "" else None,
            dias_gestion=p.dias_gestion
        )
        db.add(nuevo)
        nuevos.append(nuevo)

    db.commit()
    return {"insertados": len(nuevos)}


@router.delete("")
@router.delete("/")
def delete_all_pqrds(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    require_roles(user, ["admin"])

    deleted = db.query(models.PQRD).delete()
    db.commit()
    return {"eliminados": deleted}
