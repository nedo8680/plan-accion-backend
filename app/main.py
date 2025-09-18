from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import CORS_ORIGINS
from app.database import Base, engine, SessionLocal
from app.auth import router as auth_router
from app.routers.plans import router as plans_router
from app.deps import seed_users

app = FastAPI(title="Plan de Acción API (2 roles)", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    seed_users(db)

app.include_router(auth_router)
app.include_router(plans_router)

@app.get("/")
def root():
    return {"status": "ok"}
