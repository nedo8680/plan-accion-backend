import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response  # NEW
from app import models

from app.config import CORS_ORIGINS as CORS_ORIGINS_DEFAULT
from app.database import Base, engine, SessionLocal
from app.auth import router as auth_router
from app.routers.plans import router as planes_router
from app.deps import seed_users

Base.metadata.create_all(bind=engine)

# ──────────────────────────────────────────────────────────────────────────────
# CORS: toma de env o de config
cors_from_env = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]

# Agrega aquí tu frontend en producción y localhost 5173
DEFAULT_ALLOWED = [
    "http://localhost:5173",
    "https://lively-begonia-ccf65e.netlify.app",  # <— tu Netlify
]
ALLOW_ORIGINS = cors_from_env or CORS_ORIGINS_DEFAULT or DEFAULT_ALLOWED  

SEED_ON_START = os.getenv("SEED_ON_START", "false").lower() == "true"
# ──────────────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    if SEED_ON_START:
        with SessionLocal() as db:
            seed_users(db)
    yield

app = FastAPI(
    title="Plan de Acción API (2 roles)",
    version="1.0",
    lifespan=lifespan,
)

# (Opcional) evita redirect automático /ruta -> /ruta/
# Si lo activas, asegúrate que tus rutas existan sin slash final.
# app.router.redirect_slashes = False  # NEW (opcional)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_credentials=True,          # si no usas cookies, puedes poner False
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── PATCH CORS EN REDIRECTS ───────────────────────────────────────────
# Algunos navegadores bloquean si el 307/308 no trae CORS.
@app.middleware("http")  # NEW
async def add_cors_on_redirects(request: Request, call_next):
    resp: Response = await call_next(request)
    if resp.status_code in (301, 302, 307, 308):
        origin = request.headers.get("origin")
        if origin and origin in ALLOW_ORIGINS:
            resp.headers.setdefault("Access-Control-Allow-Origin", origin)
            resp.headers.setdefault("Vary", "Origin")
            resp.headers.setdefault("Access-Control-Allow-Credentials", "true")
    return resp
# ──────────────────────────────────────────────────────────────────────

# Routers
app.include_router(auth_router)        # /auth/token, /auth/me
app.include_router(planes_router)      # /seguimiento/*

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/healthz")
def healthz():
    return {"ok": True}
