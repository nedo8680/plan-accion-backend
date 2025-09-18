from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class PlanBase(BaseModel):
    num_plan_mejora: str
    nombre_entidad: str
    observacion_informe_calidad: Optional[str] = None
    insumo_mejora: Optional[str] = None
    tipo_accion_mejora: Optional[str] = None
    accion_mejora_planteada: Optional[str] = None
    descripcion_actividades: Optional[str] = None
    evidencia_cumplimiento: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_final: Optional[date] = None
    seguimiento: Optional[str] = None
    enlace_entidad: Optional[str] = None
    estado: Optional[str] = "Pendiente"

class PlanCreate(PlanBase):
    pass

class PlanUpdate(PlanBase):
    pass

class PlanOut(PlanBase):
    id: int
    created_by: int
    model_config = ConfigDict(from_attributes=True)
