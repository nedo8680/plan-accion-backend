from sqlalchemy import Column, Integer, String, Text, Date, Enum, ForeignKey
from app.database import Base
import enum

class UserRole(str, enum.Enum):
    usuario = "usuario"
    admin = "admin"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.usuario)

class PlanAccion(Base):
    __tablename__ = "plan_accion"
    id = Column(Integer, primary_key=True, index=True)

    num_plan_mejora = Column(String(50), nullable=False)
    nombre_entidad = Column(String(255), nullable=False)
    observacion_informe_calidad = Column(Text, nullable=True)
    insumo_mejora = Column(String(255), nullable=True)
    tipo_accion_mejora = Column(String(255), nullable=True)
    accion_mejora_planteada = Column(Text, nullable=True)
    descripcion_actividades = Column(Text, nullable=True)
    evidencia_cumplimiento = Column(Text, nullable=True)  # URL(s) o texto
    fecha_inicio = Column(Date, nullable=True)
    fecha_final = Column(Date, nullable=True)
    seguimiento = Column(String(255), nullable=True)      # Pendiente/En progreso/Finalizado
    enlace_entidad = Column(Text, nullable=True)

    estado = Column(String(50), nullable=True, default="Pendiente")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
