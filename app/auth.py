# app/auth.py
import os
from typing import Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_HOURS
from app.database import get_db
from app import models

router = APIRouter(prefix="/auth", tags=["auth"])

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ⬇️ lee el flag del entorno
DISABLE_AUTH = os.getenv("DISABLE_AUTH", "false").lower() == "true"

# ⚠️ Si auth está desactivado, no obligamos a pasar token:
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token") if not DISABLE_AUTH else (lambda: None)

def create_access_token(sub: str, role: str, user_id: int):
    payload = {
        "sub": sub,           # email
        "role": role,         # "admin" | "entity"
        "uid": user_id,       # id numérico
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def get_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme)  # ahora es opcional si DISABLE_AUTH=true
) -> models.User:
    # ⬇️ BYPASS: si está desactivada la auth, devolvemos un "usuario invitado admin"
    if DISABLE_AUTH:
        return models.User(
            id=0,
            email="guest@demo.com",
            hashed_password="",
            role=models.UserRole.admin,  # asegura permisos máximos en modo libre
        )

    cred_exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        email: str = payload.get("sub")
        uid: int | None = payload.get("uid")
        role_in_token: str | None = payload.get("role")
        if email is None or uid is None or role_in_token is None:
            raise cred_exc
    except JWTError:
        raise cred_exc

    # Resolver contra DB por id si está, si no por email (fallback)
    user = None
    if uid is not None:
        user = db.query(models.User).get(uid)
    if not user:
        user = db.query(models.User).filter_by(email=email).first()

    if not user:
        raise cred_exc
    return user

def require_roles(*roles: str):
    def checker(user: models.User = Depends(get_current_user)):
        # ⬇️ BYPASS: si auth está desactivada, permite todo
        if DISABLE_AUTH:
            return user
        # si auth activa, valida rol normalmente
        current_role = user.role.value if hasattr(user.role, "value") else user.role
        if current_role not in roles:
            raise HTTPException(status_code=403, detail="Sin permisos")
        return user
    return checker

@router.post("/token")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(email=form.username).first()
    if not user or not pwd.verify(form.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    token = create_access_token(
        user.email,
        user.role.value if hasattr(user.role, "value") else user.role,
        user.id
    )
    return {"access_token": token, "token_type": "bearer"}

# ✅ NUEVO: endpoint para que el front sepa quién es y qué rol tiene
@router.get("/me")
def me(current: models.User = Depends(get_current_user)):
    role = current.role.value if hasattr(current.role, "value") else current.role
    return {
        "id": current.id,
        "email": current.email,
        "role": role,
    }
