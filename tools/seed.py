import os, bcrypt, datetime as dt, sqlite3
from urllib.parse import urlparse

DB_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

def _connect():
    if DB_URL.startswith("sqlite:///"):
        path = DB_URL.replace("sqlite:///","")
        return sqlite3.connect(path)
    raise SystemExit("Este seed.py rápido está pensado para SQLite (ajústalo a psycopg si usas Postgres).")

def now():
    return dt.datetime.utcnow().isoformat(sep=" ", timespec="seconds")

def h(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

con = _connect()
cur = con.cursor()

# Users
cur.execute("INSERT INTO users (email, hashed_password, role, created_at, updated_at) VALUES (?,?,?,?,?)",
            ("admin@demo.com",   h("admin123"),   "admin",   now(), now()))
cur.execute("INSERT INTO users (email, hashed_password, role, created_at, updated_at) VALUES (?,?,?,?,?)",
            ("usuario@demo.com", h("usuario123"), "usuario", now(), now()))

# Plan
cur.execute("""INSERT INTO plans (nombre_entidad, objetivo, responsable, estado, owner_id, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?)""", 
            ("Alcaldía Demo", "Mejorar indicador X", "María Pérez", "En progreso", 2, now(), now()))

# Seguimiento
cur.execute("""INSERT INTO seguimiento (plan_id, evidencia_cumplimiento, fecha_inicio, fecha_final, seguimiento, enlace_entidad, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?)""", 
            (1, "Acta 001", "2025-10-01", "2025-10-05", "Inicio de actividades", "https://docs.demo/acta-001", now(), now()))

con.commit()
con.close()
print("✅ Seed completado (SQLite). Usuarios: admin@demo.com/admin123, usuario@demo.com/usuario123")
