# Plan de Acción API – FastAPI (2 roles)

Roles: **admin** y **usuario**.

## Ejecutar
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Login (x-www-form-urlencoded):
- `POST http://localhost:8000/auth/token`
  - admin: `username=admin@demo.com` `password=admin123`
  - usuario: `username=usuario@demo.com` `password=usuario123`

Usa `Authorization: Bearer <token>` en `/plans/*`.

## Endpoints
- `GET /plans` (usuario ve solo los suyos; admin ve todos)
- `POST /plans` (usuario/admin)
- `GET /plans/{id}`
- `PUT /plans/{id}` (usuario solo si es dueño; admin cualquiera)
- `POST /plans/{id}/estado?estado=En%20progreso` (solo admin)
- `DELETE /plans/{id}` (solo admin)

Configura variables en `.env` si deseas:
```
JWT_SECRET=tu-secreto
JWT_EXPIRE_HOURS=8
DATABASE_URL=sqlite:///./app.db
CORS_ORIGINS=http://localhost:5173
```
