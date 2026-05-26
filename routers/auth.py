"""
Auth router — placeholder для будущего личного кабинета.
Endpoints будут добавлены в Фазе 2.

Подключить в main.py когда будет готово:
    from routers import auth
    app.include_router(auth.router)
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/auth", tags=["auth"])

# TODO Phase 2:
# POST /api/auth/register  — регистрация (email, password, org_name)
# POST /api/auth/login     — логин, возвращает JWT
# POST /api/auth/refresh   — обновить access token
# POST /api/auth/logout    — инвалидировать refresh token
# GET  /api/auth/me        — профиль текущего пользователя
