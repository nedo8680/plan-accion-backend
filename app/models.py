from sqlalchemy import Column, Integer, String, Text, Date, Enum, ForeignKey, DateTime
from datetime import datetime
from app.database import Base
import enum
import uuid


class UserRole(str, enum.Enum):
    entidad = "entidad"
    admin = "admin"
    auditor = "auditor"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.entidad)

class PlanAccion(Base):
    __tablename__ = "plan_accion"
    id = Column(Integer, primary_key=True, index=True)
    num_plan_mejora = Column(String(50), nullable=False, default=lambda: str(uuid.uuid4())[:8])
    nombre_entidad = Column(String(255), nullable=False)
    insumo_mejora = Column(String(255), nullable=True)
    tipo_accion_mejora = Column(String(255), nullable=True)
    accion_mejora_planteada = Column(Text, nullable=True)
    descripcion_actividades = Column(Text, nullable=True)
    evidencia_cumplimiento = Column(Text, nullable=True)
    fecha_inicio = Column(Date, nullable=True)
    fecha_final = Column(Date, nullable=True)
    seguimiento = Column(String(255), nullable=True)
    enlace_entidad = Column(Text, nullable=True)
    # auditor
    observacion_calidad = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    estado = Column(String(50), nullable=True, default="Pendiente")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

class Seguimiento(Base):
    __tablename__ = "seguimiento"
    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey("plan_accion.id"), nullable=False)

    # SIN observacion_informe_calidad; SOLO el del auditor:
    observacion_calidad = Column(Text, nullable=True)

    insumo_mejora = Column(String(255), nullable=True)
    tipo_accion_mejora = Column(String(255), nullable=True)
    accion_mejora_planteada = Column(Text, nullable=True)
    descripcion_actividades = Column(Text, nullable=True)
    evidencia_cumplimiento = Column(Text, nullable=True)
    fecha_inicio = Column(Date, nullable=True)
    fecha_final = Column(Date, nullable=True)
    seguimiento = Column(String(255), nullable=True)
    enlace_entidad = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
