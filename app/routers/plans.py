from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user, require_roles

router = APIRouter(prefix="/seguimiento", tags=["seguimiento"])

# ---------------- PLANES (padre) ----------------
@router.get("")          # <— sin slash
@router.get("/")         # <— con slash
def list_planes(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
    q: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> List[schemas.PlanOut]:
    query = db.query(models.PlanAccion)
    if q:
        like = f"%{q}%"
        query = query.filter(models.PlanAccion.nombre_entidad.ilike(like))
    return (
        query.order_by(models.PlanAccion.id.desc())
        .offset(skip)
        .limit(min(limit, 200))
        .all()
    )

@router.post("")
@router.post("/")
def crear_plan(
    payload: schemas.PlanCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_roles("entidad", "admin")),
) -> schemas.PlanOut:
    plan = models.PlanAccion(**payload.model_dump(exclude_unset=True), created_by=user.id)
    db.add(plan); db.commit(); db.refresh(plan)
    return plan

@router.get("/{plan_id}")
@router.get("/{plan_id}/")
def obtener_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
) -> schemas.PlanOut:
    plan = db.query(models.PlanAccion).get(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="No encontrado")
    return plan

@router.put("/{plan_id}")
@router.put("/{plan_id}/")
def actualizar_plan(
    plan_id: int,
    payload: schemas.PlanUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
) -> schemas.PlanOut:
    plan = db.query(models.PlanAccion).get(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="No encontrado")
    # if user.role == models.UserRole.entidad and plan.created_by != user.id:
    #     raise HTTPException(status_code=403, detail="Sin permisos")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(plan, k, v)
    db.commit(); db.refresh(plan)
    return plan

@router.post("/{plan_id}/enviar_revision")
@router.post("/{plan_id}/enviar_revision/")
def enviar_revision(
    plan_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_roles("entidad", "admin")),
) -> schemas.PlanOut:
    plan = db.query(models.PlanAccion).get(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="No encontrado")
    plan.estado = "En revisión"
    db.commit(); db.refresh(plan)
    return plan

@router.post("/{plan_id}/observacion")
@router.post("/{plan_id}/observacion/")
def agregar_observacion(
    plan_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_roles("auditor", "admin")),
) -> schemas.PlanOut:
    plan = db.query(models.PlanAccion).get(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="No encontrado")
    plan.observacion_calidad = (payload.get("observacion") or "").strip()
    plan.estado = "Observado"
    db.commit(); db.refresh(plan)
    return plan

@router.post("/{plan_id}/estado")
@router.post("/{plan_id}/estado/")
def cambiar_estado(
    plan_id: int,
    estado: str = Query(..., description="Nuevo estado, p.ej. 'Observado', 'Aprobado', 'En revisión'"),
    db: Session = Depends(get_db),
    user: models.User = Depends(require_roles("auditor", "admin")),
) -> schemas.PlanOut:
    plan = db.query(models.PlanAccion).get(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="No encontrado")
    plan.estado = estado
    db.commit(); db.refresh(plan)
    return plan

@router.delete("/{plan_id}")
@router.delete("/{plan_id}/")
def eliminar_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_roles("entidad", "admin")),
):
    plan = db.query(models.PlanAccion).get(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="No encontrado")
    db.query(models.Seguimiento).filter(models.Seguimiento.plan_id == plan_id).delete()
    db.delete(plan); db.commit()
    return {"ok": True}

# ---------------- SEGUIMIENTOS (hijos) ----------------

def _assert_access(plan: models.PlanAccion, user: models.User, *, write: bool = False):
    return

@router.get("/{plan_id}/seguimiento", response_model=List[schemas.SeguimientoOut])
@router.get("/{plan_id}/seguimiento/", response_model=List[schemas.SeguimientoOut])
def listar_seguimientos(
    plan_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
) -> List[schemas.SeguimientoOut]:
    plan = db.query(models.PlanAccion).get(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    _assert_access(plan, user)
    return (
        db.query(models.Seguimiento)
        .filter(models.Seguimiento.plan_id == plan.id)
        .order_by(models.Seguimiento.id.asc())
        .all()
    )

@router.post("/{plan_id}/seguimiento", response_model=schemas.SeguimientoOut)
@router.post("/{plan_id}/seguimiento/", response_model=schemas.SeguimientoOut)
def crear_seguimiento(
    plan_id: int,
    payload: schemas.SeguimientoCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
) -> schemas.SeguimientoOut:
    plan = db.query(models.PlanAccion).get(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    _assert_access(plan, user)

    data = payload.model_dump(exclude_unset=True)
    for k in ("fecha_inicio", "fecha_final"):
        if k in data and not data[k]:
            data[k] = None

    seg = models.Seguimiento(**data, plan_id=plan.id)
    seg.updated_by_id = user.id 
    db.add(seg); db.commit()
    seg = (
        db.query(models.Seguimiento)
          .get(seg.id)
    )
    return seg

@router.put("/{plan_id}/seguimiento/{seg_id}", response_model=schemas.SeguimientoOut)
@router.put("/{plan_id}/seguimiento/{seg_id}/", response_model=schemas.SeguimientoOut)
def actualizar_seguimiento(
    plan_id: int,
    seg_id: int,
    payload: schemas.SeguimientoUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
) -> schemas.SeguimientoOut:
    plan = db.query(models.PlanAccion).get(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    _assert_access(plan, user)

    seg = db.query(models.Seguimiento).get(seg_id)
    if not seg or seg.plan_id != plan.id:
        raise HTTPException(status_code=404, detail="Seguimiento no encontrado")

    data = payload.model_dump(exclude_unset=True)
    if user.role == models.UserRole.entidad and "observacion_calidad" in data:
        del data["observacion_calidad"]

    for k, v in data.items():
        setattr(seg, k, v)
        
    if "enlace_entidad" in data:
        plan.enlace_entidad = data["enlace_entidad"]
    seg.updated_by_id = user.id
    db.commit()
    # 🔁 reconsulta con join para traer el email
    seg = (
        db.query(models.Seguimiento)
          .get(seg.id)
    )
    return seg

@router.delete("/{plan_id}/seguimiento/{seg_id}")
@router.delete("/{plan_id}/seguimiento/{seg_id}/")
def eliminar_seguimiento(
    plan_id: int,
    seg_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    plan = db.query(models.PlanAccion).get(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    _assert_access(plan, user)

    seg = db.query(models.Seguimiento).get(seg_id)
    if not seg or seg.plan_id != plan.id:
        raise HTTPException(status_code=404, detail="Seguimiento no encontrado")

    db.delete(seg); db.commit()
    return {"ok": True}
