import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS as CORS_ORIGINS_DEFAULT
from app.database import Base, engine, SessionLocal
from app.auth import router as auth_router
# si ya cambiaste el prefijo a /seguimiento, el archivo sigue siendo plans.py:
from app.routers.plans import router as planes_router  # prefix="/seguimiento"
from app.deps import seed_users

# ──────────────────────────────────────────────────────────────────────────────
# CORS: toma de env o de config
cors_from_env = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
ALLOW_ORIGINS = cors_from_env or CORS_ORIGINS_DEFAULT or ["*"]

SEED_ON_START = os.getenv("SEED_ON_START", "false").lower() == "true"
# ──────────────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: crea tablas y opcionalmente siembra
    Base.metadata.create_all(bind=engine)
    if SEED_ON_START:
        with SessionLocal() as db:
            seed_users(db)
    yield
    # Shutdown: nada especial


app = FastAPI(
    title="Plan de Acción API (2 roles)",
    version="1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router)        # /auth/token, /auth/me
app.include_router(planes_router)      # /seguimiento/* (antes era /plans)

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/healthz")
def healthz():
    return {"ok": True}
