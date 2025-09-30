from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user, require_roles


router = APIRouter(prefix="/seguimiento", tags=["seguimiento"])

@router.get("/", response_model=List[schemas.PlanOut])
def list_planes(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
    q: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
):
    query = db.query(models.PlanAccion)
    if user.role == models.UserRole.entidad:
        query = query.filter(models.PlanAccion.created_by == user.id)
    if q:
        like = f"%{q}%"
        query = query.filter(models.PlanAccion.nombre_entidad.ilike(like))
    return (
        query.order_by(models.PlanAccion.id.desc())
        .offset(skip)
        .limit(min(limit, 200))
        .all()
    )

@router.post("/", response_model=schemas.PlanOut)
def crear_plan(
    payload: schemas.PlanCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_roles("entidad","admin"))
):
    plan = models.PlanAccion(**payload.model_dump(), created_by=user.id)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan

@router.get("/{plan_id}", response_model=schemas.PlanOut)
def obtener_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    plan = db.query(models.PlanAccion).get(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="No encontrado")
    if user.role == models.UserRole.entidad and plan.created_by != user.id:
        raise HTTPException(status_code=403, detail="Sin permisos")
    return plan

@router.put("/{plan_id}", response_model=schemas.PlanOut)
def actualizar_plan(
    plan_id: int,
    payload: schemas.PlanUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    plan = db.query(models.PlanAccion).get(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="No encontrado")
    if user.role == models.UserRole.entidad and plan.created_by != user.id:
        raise HTTPException(status_code=403, detail="Sin permisos")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(plan, k, v)
    db.commit()
    db.refresh(plan)
    return plan

@router.post("/{plan_id}/estado", response_model=schemas.PlanOut)
def cambiar_estado(
    plan_id: int,
    estado: str = Query(..., description="Nuevo estado, p.ej. 'Observado', 'Aprobado', 'En progreso'"),
    db: Session = Depends(get_db),
    user: models.User = Depends(require_roles("admin"))
):
    plan = db.query(models.PlanAccion).get(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="No encontrado")
    plan.estado = estado
    db.commit()
    db.refresh(plan)
    return plan

@router.delete("/{plan_id}")
def eliminar_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_roles("admin"))
):
    plan = db.query(models.PlanAccion).get(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="No encontrado")
    db.delete(plan)
    db.commit()
    return {"ok": True}
