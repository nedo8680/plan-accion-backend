# app/dependencies.py
from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from app.settings import settings
from typing import Iterable

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        sub: str = payload.get("sub")
        role: str = payload.get("role")
        if sub is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"email": sub, "role": role}
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
def require_roles(roles: Iterable[str]):
    def _guard(current=Depends(get_current_user)):
        if current["role"] not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return current
    return _guard