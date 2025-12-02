from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user, require_roles

router = APIRouter(prefix="/habilidades", tags=["habilidades"])

# ----------- Habilidades (padre) ----------------
@router.get("")
@router.get("/")
def get_all_habilidades(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    habilidades = db.query(models.Habilidad).all()
    return habilidades

@router.get("/c1p3d6i01")
@router.get("/c1p3d6i01/")
def calcular_indicador_1(
    filtro_anio: Optional[List[int]] = Query(None),
    filtro_mes: Optional[List[int]] = Query(None),
    filtro_entidad: Optional[List[int]] = Query(None),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    # Query base
    query = db.query(models.Habilidad)

    # Aplicar filtros si existen
    if filtro_anio:
        query = query.filter(models.Habilidad.anio.in_(filtro_anio))

    if filtro_mes:
        query = query.filter(models.Habilidad.mes.in_(filtro_mes))

    if filtro_entidad:
        query = query.filter(models.Habilidad.id_entidad.in_(filtro_entidad))

    registros = query.all()

    if not registros or len(registros) == 0:
        return {"c1_p3_d6_01": 0}

    # Numerador: promedio de la calificación
    calificaciones = [r.pct_habilidades_tecnicas for r in registros if r.pct_habilidades_tecnicas is not None]
    # Denominador: cantidad total de capacitados
    capacitados = [r.num_capacitados_tecnicas for r in registros if r.num_capacitados_tecnicas is not None]

    if len(calificaciones) == 0 or len(capacitados) == 0:
        return {"c1_p3_d6_01": 0}

    indicador = sum(calificaciones) / sum(capacitados)

    return {"c1_p3_d6_01": indicador}


@router.get("/c1p3d6i02")
@router.get("/c1p3d6i02/")
def calcular_indicador_2(
    filtro_anio: Optional[List[int]] = Query(None),
    filtro_mes: Optional[List[int]] = Query(None),
    filtro_entidad: Optional[List[int]] = Query(None),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    # Query base
    query = db.query(models.Habilidad)

    # Aplicar filtros si existen
    if filtro_anio:
        query = query.filter(models.Habilidad.anio.in_(filtro_anio))

    if filtro_mes:
        query = query.filter(models.Habilidad.mes.in_(filtro_mes))

    if filtro_entidad:
        query = query.filter(models.Habilidad.id_entidad.in_(filtro_entidad))

    registros = query.all()

    if not registros or len(registros) == 0:
        return {"c1_p3_d6_02": 0}

    # Numerador: promedio de la calificación
    calificaciones = [r.pct_habilidades_socioemocionales for r in registros if r.pct_habilidades_socioemocionales is not None]
    # Denominador: cantidad total de capacitados
    capacitados = [r.num_capacitados_socioemocionales for r in registros if r.num_capacitados_socioemocionales is not None]

    if len(calificaciones) == 0 or len(capacitados) == 0:
        return {"c1_p3_d6_02": 0}

    indicador = sum(calificaciones) / sum(capacitados)

    return {"c1_p3_d6_02": indicador}


@router.post("")
@router.post("/")
def cargar_habilidades(
    payload: schemas.HabilidadEntradaLista,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    nuevos = []

    for p in payload.habilidades:
        nuevo = models.Habilidad(
            anio = p.anio,
            mes = p.mes,
            id_entidad = p.id_entidad,
            entidad = p.entidad,
            pct_habilidades_tecnicas = p.pct_habilidades_tecnicas,
            num_capacitados_tecnicas = p.num_capacitados_tecnicas,
            pct_habilidades_socioemocionales = p.pct_habilidades_socioemocionales,
            num_capacitados_socioemocionales = p.num_capacitados_socioemocionales
        )
        db.add(nuevo)
        nuevos.append(nuevo)

    db.commit()
    return {"insertados": len(nuevos)}


@router.delete("/{habilidad_id}")
@router.delete("/{habilidad_id}/")
def eliminar_habilidad(
    habilidad_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    habilidad = db.query(models.Habilidad).filter(models.Habilidad.id == habilidad_id).first()
    
    if not habilidad:
        raise HTTPException(status_code=404, detail="Habilidad no encontrada")

    db.delete(habilidad)
    db.commit()
    
    return {"message": "Habilidad eliminada exitosamente"}

@router.delete("")
@router.delete("/")
def eliminar_todas_habilidades(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    db.query(models.Habilidad).delete()
    db.commit()
    return {"message": "Todas las habilidades han sido eliminadas exitosamente"}

