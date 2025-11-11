from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user, require_roles

router = APIRouter(prefix="/reports", tags=["reports"])

# ---------------- REPORTES (padre) ----------------
@router.get("/latest")
@router.get("/latest/")
def get_latest_report(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
) -> schemas.PlanOut:
    report = db.query(models.Reporte).order_by(models.Reporte.id.desc()).first()
    if not report:
        raise HTTPException(status_code=404, detail="No report found")
    return report

@router.post("")
@router.post("/")
def create_report(
    payload: schemas.ReportCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_roles("admin", "auditor")),
) -> schemas.PlanOut:
    report = models.Reporte(**payload.model_dump(exclude_unset=True))
    db.add(report); db.commit(); db.refresh(report)
    return report

